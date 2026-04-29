# 🎙️ PodcastAI
### Enterprise-Grade PDF to Studio-Quality Audio Engine

**Developed by:** [Shabir Ahmad](https://github.com/Shabir-Ahmad-tech)  
**Institution:** University of Engineering and Applied Sciences (UEAS) Swat  
**Context:** Final Project — KPITB AI & ML Training Program  
**Location:** Kabal, Swat, Pakistan

---

## 💎 The Vision
**PodcastAI** is a high-performance automation engine designed to transform static, information-dense PDFs into engaging, dual-host audio experiences. Built for the modern professional, it bridges the gap between academic research and consumable media using a "Zero-Waste" architectural approach.

By leveraging **Gemini 2.0 Flash** for hyper-intelligent scripting and **Microsoft Neural TTS** for human-grade synthesis, PodcastAI delivers studio-quality results at a fraction of the cost of traditional production.

---

## ✨ Premium Features

- **🧠 Cognitive Scripting:** Powered by Gemini 2.0 Flash to synthesize complex documents into natural, 2-person dialogues (Alex & Sara).
- **🎭 Dual-Host Persona:** Features curated voice profiles with distinct tonalities:
    - **Alex:** The Lead Host (Warm, Authoritative, GuyNeural).
    - **Sara:** The Insightful Co-Host (Energetic, Curious, JennyNeural).
- **⚡ High-Concurrency Engine:** Utilizes Python's `asyncio` to generate and stitch audio clips in parallel, ensuring sub-60-second delivery.
- **🎨 Elite UI/UX:** A bespoke Streamlit dashboard featuring a sleek dark-mode aesthetic, optimized for clarity and flow.
- **📉 Hyper-Efficiency:** Near-zero operational overhead, processing 5,000+ words for less than $0.001.

---

## 🛠️ Technical Architecture

| Component | Technology | Role |
| :--- | :--- | :--- |
| **Frontend** | Streamlit | Bespoke Dark-Mode Interface |
| **LLM Orchestrator** | OpenRouter (Gemini 2.0 Flash) | Contextual Script Writing |
| **PDF Extraction** | PyMuPDF (Fitz) | High-Fidelity Text Parsing |
| **Voice Synthesis** | Edge-TTS (Microsoft Neural) | 100% Free, Human-Like TTS |
| **Audio Processing** | Pydub + FFmpeg | Multi-Track Stitching & Mastering |

---

## 🚀 Performance & Cost Analysis

| Metric | Traditional Podcast | PodcastAI |
| :--- | :--- | :--- |
| **Production Time** | 4 - 8 Hours | < 60 Seconds |
| **Equipment Cost** | $500 - $2,000 | $0.00 |
| **Software Cost** | $50/mo+ | Free (Open Source) |
| **API Cost (per ep)** | N/A | ~$0.001 (Gemini Flash) |

---

## 📦 Installation & Setup

### 1. System Requirements
Ensure **FFmpeg** is installed (required for audio stitching):
- **Windows:** `choco install ffmpeg`
- **macOS:** `brew install ffmpeg`

### 2. Environment Setup
```bash
# Clone and enter the workspace
git clone https://github.com/your-repo/pdf-podcast.git
cd pdf-podcast

# Initialize Virtual Environment
python -m venv .venv
source .venv/bin/activate  # Windows: .\.venv\Scripts\Activate.ps1

# Install Production Dependencies
pip install -r requirements.txt
```

### 3. Configuration
Create a `.env` file in the root directory:
```env
OPENROUTER_API_KEY=your_secured_api_key
```

### 4. Execution
```bash
streamlit run app.py
```

---

## 🛡️ License & Ethics
This project is licensed under the **MIT License**. Built with ethical AI standards in mind, ensuring transparency in synthetic media generation.

---

**Crafted with 💜 by Shabir Ahmad**  
*Building the future of AI-driven enterprise assets.*

