# PROJECT REPORT: PodcastAI
## AI-Driven PDF to Audio Synthesis Engine

**Student Name:** Shabir Ahmad  
**Institution:** University of Engineering and Applied Sciences (UEAS) Swat  
**Program:** KPITB AI & ML Training Program  
**Submission Date:** April 2026  

---

## 1. Executive Summary
PodcastAI is a high-performance automation tool developed as part of the KPITB AI & ML Training Program. The project addresses the challenge of "Information Overload" by transforming static PDF documents into engaging, studio-quality audio dialogues. By integrating state-of-the-art LLMs (Gemini 2.0 Flash) with advanced Neural Text-to-Speech (edge-tts), the system creates a dual-host podcast experience with near-zero operational costs.

---

## 2. Problem Statement
In academic and professional environments, users often struggle to consume long-form text documents (PDFs) due to time constraints or learning preferences. Existing solutions are either too robotic (traditional screen readers) or prohibitively expensive (human voiceovers). There is a significant need for a low-cost, high-quality, and automated way to convert complex text into conversational audio.

---

## 3. Objectives
- **Automation:** Fully automate the pipeline from PDF upload to MP3 download.
- **Naturalism:** Generate scripts that sound like human conversations, not just read text.
- **Cost Efficiency:** Utilize high-efficiency models like Gemini 2.0 Flash to keep costs under $0.001 per episode.
- **Speed:** Implement concurrent processing to deliver results in under 60 seconds.

---

## 4. Technical Stack
The system is built using a modern, lightweight Python stack:

| Layer | Technology | Rationale |
| :--- | :--- | :--- |
| **User Interface** | Streamlit | Rapid development of a professional, interactive dashboard. |
| **Logic/Brain** | OpenRouter (Gemini 2.0 Flash) | Optimized for speed, context window, and extreme cost-efficiency. |
| **PDF Processing** | PyMuPDF (Fitz) | High accuracy in text extraction compared to legacy libraries. |
| **Voice Synthesis** | Microsoft Neural (edge-tts) | Free, high-fidelity voices with natural prosody. |
| **Audio Mixing** | Pydub / FFmpeg | Precise control over audio stitching and silence injection. |

---

## 5. Methodology & Implementation

### 5.1 The Pipeline Architecture
The application follows a strict 4-step sequential pipeline:

1.  **Text Extraction:** The PDF is parsed into raw text. Cleaning algorithms remove artifacts like page numbers and headers to ensure clean input for the LLM.
2.  **Contextual Scriptwriting:** The text is sent to Gemini 2.0 Flash with a specialized system prompt. The model is instructed to act as a "Lead Host" and "Insightful Co-Host," creating a natural back-and-forth dialogue.
3.  **Neural Synthesis:** The script is parsed into individual speaker turns. Using Python's `asyncio`, the system calls Microsoft's Neural TTS servers concurrently for each turn, significantly reducing wait times.
4.  **Studio Mastering:** The individual clips are stitched together using `pydub`. 420ms of silence is injected between turns to simulate natural human breathing and turn-taking.

---

## 6. Key Features & Innovations
- **Asynchronous Audio Generation:** Unlike traditional systems that generate audio line-by-line, PodcastAI generates all dialogue turns simultaneously.
- **Dynamic Persona Engineering:** The AI hosts (Alex & Sara) are programmed with distinct personality traits, making the content more "sticky" and memorable.
- **Zero-Cost Scaling:** By utilizing free TTS and ultra-cheap LLMs, the project demonstrates a scalable business model for automated content creation.

---

## 7. Results & Analysis
During testing with academic papers and technical reports:
- **Accuracy:** The system successfully extracted text from complex multi-column PDFs.
- **Performance:** A 5-page PDF was converted into a 4-minute podcast in approximately 45 seconds.
- **Cost:** The total API cost per generation was consistently below $0.001 USD.

---

## 8. Challenges & Learning Outcomes
- **PDF Scrapping:** Managing complex layouts was solved by migrating from `PyPDF2` to `PyMuPDF`.
- **API Latency:** Solved by implementing `async/await` for concurrent network calls.
- **UI Design:** Leveraged Streamlit's custom CSS injection to create a premium "dark mode" interface that aligns with professional UX standards.

---

## 9. Conclusion & Future Work
PodcastAI successfully demonstrates the power of integrating specialized AI agents into a single, cohesive workflow. Future iterations will include:
- **Multi-lingual support** for regional languages.
- **Voice Cloning** integration for personalized hosts.
- **Auto-Summarization** for extremely long documents (100+ pages).

---

**Submitted by:**  
Shabir Ahmad  
*April 29, 2026*
