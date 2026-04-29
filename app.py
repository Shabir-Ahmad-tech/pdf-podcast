"""
PDF to Podcast (app.py)
================================================
STACK:
    UI      → Streamlit (pure Python)
    PDF     → PyMuPDF  (better than PyPDF2)
    LLM     → OpenRouter + Gemini 2.0 Flash (cheap + fast)
    TTS     → edge-tts  (Microsoft Neural, 100% FREE)
    Audio   → pydub + ffmpeg (stitching)

RUN:
    streamlit run app.py

COST:
    LLM  → ~$0.001 per podcast (Gemini Flash is very cheap)
    TTS  → $0.00  (edge-tts is completely free)
    TOTAL → near zero cost per podcast
"""

import io
import os
import re
import uuid
import asyncio
import requests
import fitz          # PyMuPDF
import edge_tts
import streamlit as st

from pydub import AudioSegment
from dotenv import load_dotenv
from pathlib import Path

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
load_dotenv()

OPENROUTER_KEY = os.getenv("OPENROUTER_API_KEY", "")
AI_MODEL       = "google/gemini-2.0-flash-001"   # cheap + high quality

# Microsoft Neural voices via edge-tts (completely free)
VOICES = {
    "alex": "en-US-GuyNeural",    # Male — warm, friendly
    "sara": "en-US-JennyNeural",  # Female — clear, energetic
}

OUTPUT_DIR = Path("output")
OUTPUT_DIR.mkdir(exist_ok=True)


# ─────────────────────────────────────────────
# PAGE CONFIG
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="PodcastAI - PDF to Podcast",
    layout="centered",
)

st.markdown("""
<style>
  @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

  html, body, [class*="css"] { font-family: 'Inter', sans-serif; }

  /* Background */
  .stApp { background-color: #0d0d14; color: #e4e2f0; }

  /* Headings */
  h1 { font-size: 2rem !important; font-weight: 700 !important; color: #fff !important; letter-spacing: -0.03em !important; }
  h3 { color: #c4c0e0 !important; }

  /* Subtitle */
  .subtitle { color: #6b6a88; font-size: 0.97rem; margin-bottom: 1.8rem; }

  /* File uploader */
  [data-testid="stFileUploader"] {
    background: #12121c !important;
    border: 2px dashed rgba(124,106,247,0.35) !important;
    border-radius: 16px !important;
    padding: 1rem !important;
  }

  /* Generate button */
  .stButton > button {
    background: linear-gradient(135deg, #7c6af7, #5a47d4) !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    padding: 0.8rem 1.5rem !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    width: 100% !important;
    letter-spacing: 0.01em !important;
  }
  .stButton > button:hover { opacity: 0.88 !important; }

  /* Divider */
  hr { border-color: #1e1e2e !important; margin: 1.5rem 0 !important; }

  /* Audio */
  audio { width: 100%; border-radius: 10px; margin-top: 0.4rem; accent-color: #7c6af7; }

  /* Footer */
  .footer { text-align: center; font-size: 0.76rem; color: #3a3a55; margin-top: 2rem; }
</style>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────
# PIPELINE FUNCTIONS
# ─────────────────────────────────────────────

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
        raise ValueError(
            "No text found. This PDF may be image/scanned. "
            "Please use a text-based PDF."
        )
    return text


def generate_script(text: str) -> str:
    """Step 2 — Call OpenRouter (Gemini Flash) to write a podcast script."""
    if not OPENROUTER_KEY:
        raise ValueError("OPENROUTER_API_KEY is missing from your .env file.")

    # Trim to avoid token overflow (~4000 chars ≈ ~1000 tokens)
    trimmed = text[:5000]

    prompt = f"""You are a professional podcast scriptwriter.

Turn the content below into a natural, engaging 4-5 minute podcast conversation between:
- Alex: the main host. Explains clearly, uses simple language.
- Sara: the co-host. Asks great questions, adds insights, reacts naturally.

TONE: Conversational, warm, and educational. Not robotic or academic.
Use natural phrases like: "That's really interesting!", "So basically what you're saying is...", "Right, and the key thing here is..."

FORMAT — follow exactly, no exceptions:
Alex: [dialogue]
Sara: [dialogue]
Alex: [dialogue]
...

RULES:
- 12 to 18 exchanges total
- No bullet points, no markdown, no asterisks, no stage directions
- Each line must start with "Alex:" or "Sara:"
- Total script: 600-900 words
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


def parse_script(script: str) -> list[dict]:
    """Step 3 — Parse the LLM output into a list of speaker turns."""
    turns = []
    for line in script.splitlines():
        line = line.strip()
        if not line:
            continue
        if line.lower().startswith("alex:"):
            text = line[5:].strip()
            if text:
                turns.append({"speaker": "alex", "text": text})
        elif line.lower().startswith("sara:"):
            text = line[5:].strip()
            if text:
                turns.append({"speaker": "sara", "text": text})

    if not turns:
        raise ValueError(
            "Could not parse the script — unexpected AI format. "
            "Please try generating again."
        )
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


def generate_audio(turns: list, progress_bar, status_text) -> bytes:
    """Step 4 — Generate all TTS clips and stitch into one MP3."""
    session_id = uuid.uuid4().hex[:8]

    # Generate all clips
    status_text.markdown("🎤 Generating voices with Microsoft Neural TTS...")
    clip_paths = asyncio.run(_generate_all_clips(turns, session_id))
    progress_bar.progress(0.7)

    # Stitch clips
    status_text.markdown("🎚 Mixing all clips into final MP3...")
    combined = AudioSegment.empty()
    silence  = AudioSegment.silent(duration=420)

    for path in clip_paths:
        if os.path.exists(path):
            clip = AudioSegment.from_mp3(path)
            combined += clip + silence

    # Export to bytes
    buf = io.BytesIO()
    combined.export(buf, format="mp3", bitrate="128k")
    audio_bytes = buf.getvalue()

    # Cleanup clips
    for path in clip_paths:
        if os.path.exists(path):
            os.remove(path)

    progress_bar.progress(1.0)
    status_text.markdown("✅ **Audio ready!**")
    return audio_bytes


# ─────────────────────────────────────────────
# STREAMLIT UI
# ─────────────────────────────────────────────

def main():

    # ── Header ──
    st.markdown("# PodcastAI")
    st.markdown(
        '<p class="subtitle"><strong>KPITB AI & ML Training - Final Project</strong><br>'
        'Developed by: Shabir Ahmad (UEAS Swat) | Kabal, Swat<br>'
        'Upload any PDF to generate a high-quality AI podcast using Gemini Flash & Microsoft Neural voices.</p>',
        unsafe_allow_html=True
    )

    # ── API Key Warning ──
    if not OPENROUTER_KEY:
        st.warning(
            "OPENROUTER_API_KEY not found. "
            "Create a .env file with your key to get started."
        )

    st.divider()

    # ── File Upload ──
    uploaded = st.file_uploader(
        "Drop your PDF here",
        type=["pdf"],
        help="Text-based PDFs only. Scanned/image PDFs won't work.",
    )

    if uploaded:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.success(f"File {uploaded.name} ready to convert")
        with col2:
            st.caption(f"{uploaded.size / 1024:.1f} KB")

    st.markdown("")  # spacing

    # ── Generate Button ──
    if st.button("Generate Podcast", disabled=not uploaded):

        st.divider()

        # Step 1: Extract PDF text
        with st.status("Step 1 - Scanning PDF...", expanded=True) as s:
            try:
                text = extract_text(uploaded.read())
                st.write(f"Extracted {len(text):,} characters from {uploaded.name}")
                s.update(label="Step 1 - PDF scanned", state="complete")
            except Exception as e:
                s.update(label="❌ Step 1 failed", state="error")
                st.error(str(e))
                st.stop()

        # Step 2: Generate script
        with st.status("Step 2 - Writing script with Gemini AI...", expanded=True) as s:
            try:
                script = generate_script(text)
                st.write(f"Script written - {len(script):,} characters")
                with st.expander("Preview script"):
                    st.text(script[:1000] + ("..." if len(script) > 1000 else ""))
                s.update(label="Step 2 - Script written", state="complete")
            except Exception as e:
                s.update(label="❌ Step 2 failed", state="error")
                st.error(str(e))
                st.stop()

        # Step 3: Parse script
        with st.status("Step 3 - Parsing dialogue...", expanded=True) as s:
            try:
                turns = parse_script(script)
                st.write(f"Found {len(turns)} speaking turns - Alex & Sara")
                s.update(label="Step 3 - Dialogue parsed", state="complete")
            except Exception as e:
                s.update(label="❌ Step 3 failed", state="error")
                st.error(str(e))
                st.stop()

        # Step 4: Generate audio
        st.markdown("#### Step 4 - Generating voices and mixing audio...")
        progress = st.progress(0.0)
        status_txt = st.empty()
        progress.progress(0.1)

        try:
            audio_bytes = generate_audio(turns, progress, status_txt)
        except Exception as e:
            st.error(f"❌ Audio generation failed: {e}")
            st.stop()

        # ── Result ──
        st.divider()
        st.success("Your podcast is ready!")

        st.audio(audio_bytes, format="audio/mp3")

        filename = f"podcast_{uuid.uuid4().hex[:8]}.mp3"
        st.download_button(
            label="Download MP3",
            data=audio_bytes,
            file_name=filename,
            mime="audio/mpeg",
            use_container_width=True,
        )

        size_kb = len(audio_bytes) / 1024
        st.caption(
            f"📊 {len(turns)} exchanges · {size_kb:.0f} KB · "
            f"Powered by Gemini Flash + edge-tts (FREE)"
        )

    # ── Footer ──
    st.divider()
    st.markdown(
        '<p class="footer">KPITB AI & ML Final Project | Shabir Ahmad | UEAS Swat | Kabal, Swat</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
