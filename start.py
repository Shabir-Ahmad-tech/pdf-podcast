import os
import subprocess
import webbrowser
import time
import sys
from pathlib import Path

def check_ffmpeg():
    try:
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def main():
    print("🚀 Starting PodcastAI Premium Studio...")
    
    # 1. Check FFmpeg
    if not check_ffmpeg():
        print("\n❌ ERROR: FFmpeg not found!")
        print("This app requires FFmpeg to stitch audio clips together.")
        print("Please install it via: choco install ffmpeg")
        print("Or download from: https://ffmpeg.org/download.html and add to PATH.")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # 2. Path Setup
    root_dir = Path(__file__).parent
    venv_python = root_dir / ".venv" / "Scripts" / "python.exe"
    
    if not venv_python.exists():
        print(f"❌ ERROR: Virtual environment not found at {venv_python}")
        print("Please run: python -m venv .venv && pip install -r requirements.txt")
        input("\nPress Enter to exit...")
        sys.exit(1)

    # 3. Start Backend
    print("📡 Launching FastAPI Backend...")
    # Using subprocess.Popen so it runs in the background
    backend_proc = subprocess.Popen(
        [str(venv_python), "-m", "uvicorn", "backend:app", "--port", "8000"],
        cwd=str(root_dir)
    )

    # 4. Wait for server to warm up
    print("⏳ Waiting for server to initialize...")
    time.sleep(3)

    # 5. Open Browser
    print("🌐 Opening Premium UI in your browser...")
    webbrowser.open("http://localhost:8000")

    print("\n✅ APP IS RUNNING!")
    print("Keep this window open to see server logs.")
    print("Press Ctrl+C to stop the server.")

    try:
        backend_proc.wait()
    except KeyboardInterrupt:
        print("\n🛑 Stopping server...")
        backend_proc.terminate()

if __name__ == "__main__":
    main()
