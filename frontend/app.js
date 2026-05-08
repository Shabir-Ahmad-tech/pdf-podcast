const dropzone = document.getElementById('dropzone');
const fileInput = document.getElementById('fileInput');
const styleSelector = document.getElementById('styleSelector');
const progressContainer = document.getElementById('progress-container');
const progressBar = document.getElementById('progress-bar');
const statusText = document.getElementById('status-text');
const terminalContainer = document.getElementById('terminal-container');
const terminalContent = document.getElementById('terminal-content');
const playerContainer = document.getElementById('player-container');
const audioPlayer = document.getElementById('audio-player');
const downloadBtn = document.getElementById('download-btn');

// Drag & Drop Handlers
dropzone.addEventListener('dragover', (e) => {
    e.preventDefault();
    dropzone.classList.add('dragover');
});

dropzone.addEventListener('dragleave', () => {
    dropzone.classList.remove('dragover');
});

dropzone.addEventListener('drop', (e) => {
    e.preventDefault();
    dropzone.classList.remove('dragover');
    const files = e.dataTransfer.files;
    if (files.length > 0 && files[0].type === "application/pdf") {
        handleUpload(files[0]);
    } else {
        showError("Please upload a PDF file.");
    }
});

dropzone.addEventListener('click', () => {
    fileInput.click();
});

fileInput.addEventListener('change', (e) => {
    if (e.target.files.length > 0) {
        handleUpload(e.target.files[0]);
    }
});

function showError(message) {
    const errorDiv = document.createElement('div');
    errorDiv.className = 'error-message';
    errorDiv.innerHTML = `
        <div style="background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3); border-radius: 8px; padding: 1rem; margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <svg style="width: 20px; height: 20px; color: #ef4444;" fill="none" stroke="currentColor" viewBox="0 0 24 24" xmlns="http://www.w3.org/2000/svg"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>
                <strong style="color: #ef4444;">Error</strong>
            </div>
            <p style="color: #fca5a5; margin: 0;">${message}</p>
        </div>
    `;
    
    // Insert at the top of the studio section
    const studioSection = document.querySelector('.studio-section');
    studioSection.insertBefore(errorDiv, studioSection.firstChild);
    
    // Auto-remove after 5 seconds
    setTimeout(() => {
        if (errorDiv.parentNode) {
            errorDiv.remove();
        }
    }, 5000);
}

function logToTerminal(message, type = 'info') {
    const time = new Date().toLocaleTimeString([], { hour12: false, hour: '2-digit', minute: '2-digit', second: '2-digit' });
    const line = document.createElement('div');
    
    let prefix = '';
    let color = '#4ade80'; // Default green for info
    
    switch(type) {
        case 'error':
            prefix = 'ERR';
            color = '#ef4444';
            break;
        case 'warning':
            prefix = 'WRN';
            color = '#f59e0b';
            break;
        case 'success':
            prefix = 'SUC';
            color = '#10b981';
            break;
        case 'system':
            prefix = 'SYS';
            color = '#06b6d4';
            break;
        default:
            prefix = 'INF';
            color = '#8b5cf6';
    }
    
    line.innerHTML = `<span style="color: #666">[${time}]</span> <span style="color: ${color}">${prefix}:</span> ${message}`;
    terminalContent.appendChild(line);
    terminalContent.scrollTop = terminalContent.scrollHeight;
}

function updateSteps(progress) {
    const steps = [
        { id: 'step-1', val: 25 },
        { id: 'step-2', val: 50 },
        { id: 'step-3', val: 80 },
        { id: 'step-4', val: 100 }
    ];

    steps.forEach(s => {
        const el = document.getElementById(s.id);
        if (progress >= s.val) {
            el.classList.add('active', 'complete');
        } else if (progress > (s.val - 25)) {
            el.classList.add('active');
            el.classList.remove('complete');
        } else {
            el.classList.remove('active', 'complete');
        }
    });
}

async function handleUpload(file) {
    dropzone.classList.add('hidden');
    progressContainer.classList.remove('hidden');
    terminalContainer.classList.remove('hidden');
    playerContainer.classList.add('hidden');
    terminalContent.innerHTML = ''; // clear terminal
    
    // Add some visual feedback
    progressBar.style.width = '10%';
    statusText.innerText = 'Preparing upload...';
    updateSteps(10);
    
    logToTerminal(`Initializing upload for ${file.name}...`, 'system');
    logToTerminal(`File size: ${(file.size / 1024 / 1024).toFixed(2)} MB`, 'info');
    logToTerminal(`Selected style: ${styleSelector.options[styleSelector.selectedIndex].text}`, 'info');
    
    const formData = new FormData();
    formData.append('file', file);
    formData.append('style', styleSelector.value);

    try {
        logToTerminal('Connecting to neural processing server...', 'system');
        
        const response = await fetch('/api/upload', {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            const data = await response.json();
            throw new Error(data.detail || "Upload failed");
        }

        const { job_id } = await response.json();
        logToTerminal(`Job ${job_id} assigned. Starting neural pipeline...`, 'success');
        logToTerminal('Stage 1: PDF text extraction initialized', 'info');
        
        progressBar.style.width = '25%';
        statusText.innerText = 'Extracting text from PDF...';
        updateSteps(25);
        
        listenToProgress(job_id);

    } catch (err) {
        logToTerminal(`CRITICAL ERROR: ${err.message}`, 'error');
        showError("Upload failed: " + err.message);
        // Reset UI on fatal error after a delay
        setTimeout(resetUI, 3000);
    }
}

let lastStatus = "";

function listenToProgress(jobId) {
    const eventSource = new EventSource(`/api/status/${jobId}`);

    eventSource.onmessage = (event) => {
        const data = JSON.parse(event.data);

        if (data.error) {
            eventSource.close();
            logToTerminal(`PIPELINE FAILURE: ${data.error}`, 'error');
            showError("Error: " + data.error);
            setTimeout(resetUI, 3000);
            return;
        }

        progressBar.style.width = `${data.progress}%`;
        statusText.innerText = data.status;
        updateSteps(data.progress);

        if (data.status !== lastStatus) {
            logToTerminal(data.status);
            lastStatus = data.status;
        }

        if (data.status === "Complete") {
            eventSource.close();
            logToTerminal("Audio mastering finished. Ready for playback.");
            setTimeout(() => {
                progressContainer.classList.add('hidden');
                terminalContainer.classList.add('hidden');
                playerContainer.classList.remove('hidden');
                audioPlayer.src = data.audio_url;
                downloadBtn.href = data.audio_url;
            }, 1200);
        } else if (data.status === "Error") {
            eventSource.close();
            logToTerminal(`ERROR: ${data.error}`, 'error');
            showError("Processing error: " + data.error);
            setTimeout(resetUI, 3000);
        }
    };

    eventSource.onerror = () => {
        eventSource.close();
        logToTerminal("Network connection interrupted.");
        alert("Lost connection to server.");
        setTimeout(resetUI, 3000);
    };
}

function resetUI() {
    dropzone.classList.remove('hidden');
    progressContainer.classList.add('hidden');
    terminalContainer.classList.add('hidden');
    playerContainer.classList.add('hidden');
    progressBar.style.width = '0%';
    statusText.innerText = 'Initializing...';
    lastStatus = "";
    // BUG FIX: Clear file input so the same file can be re-uploaded
    fileInput.value = '';
}

// ─── Scroll Reveal Animation ─────────────────────────────────────────────────
// Animates elements with the 'reveal' class as they enter the viewport
const revealObserver = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.classList.add('visible');
            revealObserver.unobserve(entry.target); // Fire once
        }
    });
}, { threshold: 0.15 });

document.querySelectorAll('.reveal').forEach(el => revealObserver.observe(el));
