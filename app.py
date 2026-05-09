import asyncio
import io
import os
import re
import uuid
import json
import logging
import subprocess
from typing import Dict
from pathlib import Path

from fastapi import FastAPI, File, UploadFile, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import fitz         
import edge_tts
from pydub import AudioSegment
import requests
from dotenv import load_dotenv

# RAG Imports
# langchain_text_splitters is the correct package for LangChain >= 0.2
try:
    from langchain_text_splitters import RecursiveCharacterTextSplitter
except ImportError:
    from langchain.text_splitter import RecursiveCharacterTextSplitter  # Legacy fallback

from langchain_community.vectorstores import Chroma

# Use langchain-huggingface if installed, fall back to community package
try:
    from langchain_huggingface import HuggingFaceEmbeddings
except ImportError:
    from langchain_community.embeddings import HuggingFaceEmbeddings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
AI_MODEL = "meta-llama/llama-3.1-8b-instruct"

# Initialize Embeddings (Local & Free)
logger.info("Loading Embedding Model...")
embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
logger.info("Embeddings Ready.")

VOICES = {
    "alex": "en-US-GuyNeural",    # Male — warm, friendly
    "sara": "en-US-JennyNeural",  # Female — clear, energetic
}

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)

app = FastAPI(title="PodcastAI API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# In-memory job store for SSE progress tracking
jobs: Dict[str, dict] = {}

def extract_text(pdf_bytes: bytes) -> str:
    """Step 1 — Extract text from PDF using PyMuPDF."""
    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    pages_text = []
    for page in doc:
        pages_text.append(page.get_text())
    doc.close()

    text = "\n".join(pages_text)
    text = re.sub(r'\n{3,}', '\n\n', text).strip()

    if not text:
        raise ValueError("No text found. This PDF may be image/scanned. Please use a text-based PDF.")
    return text

def generate_script(text: str, style: str = "professional") -> str:
    """Step 2 — Call OpenRouter (llama 3.1) to write a podcast script."""
    if not OPENROUTER_KEY:
        raise ValueError("OPENROUTER_API_KEY is missing from your .env file.")

    # Trim to avoid token overflow (~4000 chars ≈ ~1000 tokens)
    trimmed = text[:5000]

    style_instructions = {
        "professional": "TONE: Conversational, warm, and educational. Like an NPR documentary.",
        "humorous": "TONE: Energetic, funny, and highly engaging. Use wit and banter. Like a late-night talk show.",
        "deep_dive": "TONE: Analytical, serious, and comprehensive. Focus on the nuances. Like a technical seminar."
    }

    selected_style = style_instructions.get(style, style_instructions["professional"])

    prompt = f"""You are a professional podcast scriptwriter.
    
Turn the content below into a natural, engaging 2-3 minute podcast conversation between:
- Alex: the main host. Explains clearly, uses simple language.
- Sara: the co-host. Asks great questions, adds insights, reacts naturally.

{selected_style}
Use natural phrases like: "That's really interesting!", "Right, and the key thing is..."

FORMAT — follow exactly, no exceptions:
Alex: [dialogue]
Sara: [dialogue]
...

RULES:
- 10 to 12 exchanges total
- No bullet points, no markdown outside of speaker names, no stage directions
- Total script: 400-600 words
- End with each host giving a short key takeaway

CONTENT:
{trimmed}

Write the podcast script now:"""

    response = requests.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {OPENROUTER_KEY}",
            "Content-Type": "application/json",
        },
        json={
            "model": AI_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1800,
            "temperature": 0.8,
        },
        timeout=90,
    )

    if response.status_code != 200:
        raise ValueError(f"OpenRouter API error {response.status_code}: {response.text}")

    script = response.json()["choices"][0]["message"]["content"].strip()
    if not script:
        raise ValueError("AI returned an empty script. Please try again.")

    return script

def get_rag_context(text: str, query: str = "Give me the most important parts of this document for a podcast discussion.") -> str:
    """RAG Step — Chunk, Embed, and Retrieve context."""
    # 1. Chunking
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
    chunks = text_splitter.split_text(text)
    
    # 2. In-memory Vector Store (Ephemeral for the session)
    vectorstore = Chroma.from_texts(
        texts=chunks, 
        embedding=embeddings,
        collection_name=f"pod_{uuid.uuid4().hex[:8]}"
    )
    
    # 3. Retrieval
    docs = vectorstore.similarity_search(query, k=5)
    context = "\n\n".join([doc.page_content for doc in docs])
    
    # Cleanup vectorstore (optional for ephemeral)
    vectorstore.delete_collection()
    
    return context

def parse_script(script: str) -> list[dict]:
    """Step 3 — Parse the LLM output into a list of speaker turns. Robust regex version."""
    turns = []
    for line in script.splitlines():
        line = line.strip()
        if not line:
            continue
            
        # Match lines like "Alex:", "**Alex:**", "Sara: ", etc.
        match = re.match(r'^\s*\**([A-Za-z]+)\**\s*:\s*(.*)', line, re.IGNORECASE)
        if match:
            speaker = match.group(1).lower()
            text = match.group(2).strip()
            if speaker in VOICES and text:
                turns.append({"speaker": speaker, "text": text})

    if not turns:
        raise ValueError("Could not parse the script — unexpected AI format.")
    return turns

async def _tts_clip(text: str, voice: str, path: str):
    """Generate a single TTS clip using edge-tts."""
    communicate = edge_tts.Communicate(text=text, voice=voice)
    await communicate.save(path)

async def _generate_all_clips(turns: list, session_id: str) -> list[str]:
    """Generate all TTS clips concurrently for speed."""
    paths = []
    tasks = []
    for i, turn in enumerate(turns):
        voice = VOICES[turn["speaker"]]
        path = str(OUTPUT_DIR / f"{session_id}_clip_{i:03d}.mp3")
        paths.append(path)
        tasks.append(_tts_clip(turn["text"], voice, path))

    await asyncio.gather(*tasks)
    return paths

def stitch_audio(clip_paths: list) -> bytes:
    """Stitch clips with pydub."""
    # Explicit FFmpeg check
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        raise RuntimeError("FFmpeg not found on system. Please install FFmpeg to enable audio stitching.")

    combined = AudioSegment.empty()
    silence  = AudioSegment.silent(duration=420)

    for path in clip_paths:
        if os.path.exists(path):
            clip = AudioSegment.from_mp3(path)
            combined += clip + silence

    buf = io.BytesIO()
    combined.export(buf, format="mp3", bitrate="128k")
    
    # Cleanup
    for path in clip_paths:
        if os.path.exists(path):
            try:
                os.remove(path)
            except Exception as e:
                logger.error(f"Failed to delete {path}: {e}")

    return buf.getvalue()


async def process_job(job_id: str, pdf_bytes: bytes, style: str):
    """Background task to run the entire pipeline and update job state."""
    try:
        jobs[job_id]["status"] = "Extracting knowledge from PDF..."
        text = extract_text(pdf_bytes)
        jobs[job_id]["progress"] = 15
        
        jobs[job_id]["status"] = "Indexing Knowledge Base (RAG)..."
        # We perform RAG to get the most dense, relevant info
        context = get_rag_context(text)
        jobs[job_id]["progress"] = 30
        
        jobs[job_id]["status"] = f"Synthesizing {style} script with Llama 3.1..."
        script = generate_script(context, style)
        jobs[job_id]["progress"] = 50
        jobs[job_id]["script"] = script
        
        jobs[job_id]["status"] = "Parsing dialogue..."
        turns = parse_script(script)
        jobs[job_id]["progress"] = 60
        
        jobs[job_id]["status"] = "Synthesizing Microsoft Neural Voices..."
        clip_paths = await _generate_all_clips(turns, job_id)
        jobs[job_id]["progress"] = 80
        
        jobs[job_id]["status"] = "Mastering final audio..."
        # Pydub export is blocking, run in executor
        loop = asyncio.get_running_loop()
        audio_bytes = await loop.run_in_executor(None, stitch_audio, clip_paths)
        
        # Save final audio
        out_path = OUTPUT_DIR / f"{job_id}.mp3"
        with open(out_path, "wb") as f:
            f.write(audio_bytes)
            
        jobs[job_id]["progress"] = 100
        jobs[job_id]["status"] = "Complete"
        jobs[job_id]["audio_url"] = f"/api/audio/{job_id}.mp3"
        
    except Exception as e:
        logger.error(f"Job {job_id} failed: {e}")
        jobs[job_id]["status"] = "Error"
        jobs[job_id]["error"] = str(e)


@app.post("/api/upload")
async def upload_pdf(background_tasks: BackgroundTasks, file: UploadFile = File(...), style: str = "professional"):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")
        
    pdf_bytes = await file.read()
    job_id = uuid.uuid4().hex[:8]
    
    jobs[job_id] = {
        "id": job_id,
        "status": "Initializing...",
        "progress": 0,
        "error": None,
        "audio_url": None,
        "script": None
    }
    
    background_tasks.add_task(process_job, job_id, pdf_bytes, style)
    return {"job_id": job_id}


@app.get("/api/status/{job_id}")
async def get_status(job_id: str):
    async def event_generator():
        while True:
            if job_id not in jobs:
                yield f"data: {json.dumps({'error': 'Job not found'})}\n\n"
                break
                
            job = jobs[job_id]
            yield f"data: {json.dumps(job)}\n\n"
            
            if job["status"] == "Complete" or job["status"] == "Error":
                break
                
            await asyncio.sleep(0.5)
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")


@app.get("/api/audio/{filename}")
async def get_audio(filename: str):
    file_path = OUTPUT_DIR / filename
    if not file_path.exists():
        raise HTTPException(status_code=404, detail="Audio not found")
    return FileResponse(file_path, media_type="audio/mpeg", filename=filename)


# Mount frontend static files last so it acts as a catch-all for index.html
frontend_dir = Path(__file__).parent / "frontend"
if not frontend_dir.exists():
    frontend_dir.mkdir(exist_ok=True)
app.mount("/", StaticFiles(directory=str(frontend_dir), html=True), name="frontend")
