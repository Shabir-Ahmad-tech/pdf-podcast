# PodcastAI 🎙️

> Transform any PDF into a studio-quality, dual-host audio podcast in under 60 seconds.

[![Live Demo](https://img.shields.io/badge/Live%20Demo-Streamlit-FF4B4B?style=for-the-badge&logo=streamlit)](https://pdf-podcast.streamlit.app/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow?style=for-the-badge)](LICENSE)
[![Gemini](https://img.shields.io/badge/Powered%20by-Gemini%202.0%20Flash-4285F4?style=for-the-badge&logo=google)](https://deepmind.google/technologies/gemini/)

---

## The Problem

Reading research papers and long documents is slow, isolating, and mentally exhausting. Traditional podcast production costs $500–$2,000 in equipment and 4–8 hours of studio time per episode.

**There had to be a better way.**

---

## The Solution

PodcastAI is an open-source audio intelligence engine that converts any PDF into a natural, engaging two-host podcast — complete with distinct voice personalities, fluid dialogue, and professional audio quality — for less than $0.001 per episode.

No studio. No equipment. No hours of editing. Just upload and listen.

---

## Live Demo

**[▶ Try it now → pdf-podcast.streamlit.app](https://pdf-podcast.streamlit.app/)**

Upload any PDF. Hit generate. Your podcast is ready in under 60 seconds.

---

## How It Works

```
PDF Upload → Text Extraction → AI Script Generation → Dual-Voice Synthesis → Audio Stitching → Podcast Ready
```

1. **Extract** — PyMuPDF parses the PDF with high-fidelity text extraction
2. **Script** — Gemini 2.0 Flash converts the content into a natural two-host dialogue
3. **Synthesize** — Microsoft Neural TTS renders two distinct voice personalities in parallel
4. **Stitch** — Pydub + FFmpeg merges the audio tracks into a single clean episode

---

## Meet the Hosts

| Host | Voice | Personality |
|------|-------|-------------|
| **Alex** | GuyNeural (Microsoft) | Lead host — warm, authoritative, drives the narrative |
| **Sara** | JennyNeural (Microsoft) | Co-host — curious, energetic, asks the right questions |

The dialogue sounds like a real conversation — not a text-to-speech reading.

---

## Technical Architecture

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Frontend | Streamlit | Dark-mode UI, file upload, audio playback |
| LLM | Gemini 2.0 Flash via OpenRouter | Intelligent script generation |
| PDF Parsing | PyMuPDF (Fitz) | Accurate text extraction |
| Voice Synthesis | Edge-TTS (Microsoft Neural) | Human-grade, zero-cost TTS |
| Audio Processing | Pydub + FFmpeg | Parallel rendering and multi-track stitching |
| Concurrency | Python asyncio | Sub-60-second generation via parallel audio clips |

---

## Performance

| Metric | Traditional Production | PodcastAI |
|--------|----------------------|-----------|
| Production Time | 4–8 Hours | **< 60 Seconds** |
| Equipment Cost | $500–$2,000 | **$0** |
| Software Cost | $50+/month | **Free (Open Source)** |
| API Cost per Episode | N/A | **~$0.001** |
| Words Processed | Manual | **5,000+ words** |

---

## Quickstart

### Prerequisites

FFmpeg must be installed for audio stitching:

```bash
# Windows
choco install ffmpeg

# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt install ffmpeg
```

### Installation

```bash
# Clone the repository
git clone https://github.com/Shabir-Ahmad-tech/pdf-podcast.git
cd pdf-podcast

# Create and activate virtual environment
python -m venv .venv
source .venv/bin/activate        # macOS/Linux
.\.venv\Scripts\Activate.ps1    # Windows

# Install dependencies
pip install -r requirements.txt
```

### Configuration

Create a `.env` file in the root directory:

```env
OPENROUTER_API_KEY=your_api_key_here
```

Get your free API key at [openrouter.ai](https://openrouter.ai)

### Run

```bash
streamlit run app.py
```

Open `http://localhost:8501` in your browser.

---

## Use Cases

- **Students** — Convert research papers into podcasts for commute listening
- **Professionals** — Turn dense reports into digestible audio briefings
- **Researchers** — Process academic literature at scale without reading fatigue
- **Content Creators** — Rapidly prototype podcast episodes from written content

---

## Roadmap

- [ ] Podcast style selector — Deep Dive / Hot Take / ELI5 modes
- [ ] Listener questions — Ask the hosts follow-up questions post-generation
- [ ] Multi-document comparison — Generate crossover episodes from two PDFs
- [ ] Chapter-level generation — Generate audio for specific sections only
- [ ] Export as RSS feed — Publish directly to podcast platforms

---

## Project Structure

```
pdf-podcast/
├── app.py              # Main Streamlit application
├── requirements.txt    # Python dependencies
├── packages.txt        # System-level packages (FFmpeg)
├── .python-version     # Python version pin
├── .env                # API keys (not committed)
└── README.md
```

---

## Contributing

Pull requests are welcome. For major changes, open an issue first to discuss what you'd like to change.

---

## License

MIT License — see [LICENSE](LICENSE) for details.

---

## Author

**Shabir Ahmad**
- GitHub: [@Shabir-Ahmad-tech](https://github.com/Shabir-Ahmad-tech)
- Portfolio: [shabir-ahmad.netlify.app](https://shabir-ahmad.netlify.app)
- University of Engineering and Applied Sciences (UEAS), Swat

---

*Built to make knowledge accessible — one podcast at a time.*