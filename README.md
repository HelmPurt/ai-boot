# AI Boot: FastAPI + LLaMA + MongoDB (Dockerized)

Welcome to **AI Boot** — a locally optimized FastAPI application powered by [llama-cpp-python], designed for responsive LLaMA inference and detailed analytics logging via MongoDB.

Crafted to run seamlessly on Windows 11 using Docker Desktop, with support for Kubernetes scaling.

## Features

- Dual-response generation using LLaMA (Mistral)
- MongoDB logging of prompts, responses, environment, tone, and sentiment
- Dockerized setup with hot-reload and health checks
- Minimal web interface via HTML templating
- Diagnostics for tone, sentiment, complexity, truncation, emotion trace
- Configurable via `.env` file with volume-mounted model

---

## Windows Setup: llama-cpp-python Compilation

Because `llama-cpp-python` must be compiled locally on Windows, you’ll need to install **Visual Studio Build Tools** and make sure `nmake.exe` is available in your environment.

### Steps

1. **Install Build Tools**
   - [Download Visual Studio Build Tools](https://visualstudio.microsoft.com/downloads/#build-tools-for-visual-studio)
   - Include the **C++ Build Tools** workload during setup

2. **Find `nmake.exe`**
   - Use PowerShell:
     ```powershell
     Get-ChildItem -Path "C:\Program Files (x86)\Microsoft Visual Studio" -Recurse -Include nmake.exe
     ```

3. **Add `nmake.exe` to PATH**
   - Go to System Properties → Environment Variables
   - Add the path where `nmake.exe` resides

4. **Install llama-cpp-python**
powershell
   pip install llama-cpp-python --force-reinstall --no-cache-dir
 Getting Started
 Clone the repository
powershell
 git clone https://github.com/<your-username>/ai-boot.git
 cd ai-boot
Add your model
 Place mistral.gguf into:
   models/mistral.gguf
This folder is volume-mounted and safely excluded via .gitignore

Create a .env file
env
MODEL_PATH=/app/models/mistral.gguf
MONGO_URL=mongodb://mongo:27017
API_KEY=your-secret-key  # optional

Run with Docker
powershell
docker compose up --build
App will be live at http://localhost:5001 

📁 Project Structure
ai-boot/
├── app/
│   ├── main.py
│   ├── requirements.txt
│   ├── requirements-dev.txt
│   ├── templates/
│   └── img/
├── models/             # .gguf model file (ignored by Git)
├── .env                # env config
├── Dockerfile
├── docker-compose.yml
└── README.md

models/    <---  .gguf model file must renamed in mistral.gguf

API Endpoints
    Endpoint	Method	Purpose
    /	GET	Simple homepage greeting
    /health	GET	Health check
    /chat	POST	JSON-based prompt (2 responses)
    /webchat	GET/POST	Submit via web form

MongoDB Logging
Logs analytics for each prompt:
    UTC + local timestamps
    Two raw responses from LLaMA
    Host diagnostics (cpu, OS, WSL detection)
    Tone, sentiment, emotion trace, truncation check
    Flags like HIGH_CPU if usage is high
    Stored under:
    MongoDB → llama_logs → analytics

Consider extending your app with:
    CI/CD using GitHub Actions
    Token-authentication for inference endpoints
    Pytest-powered unit tests
    Version control for model updates
    via Kubernetes or cloud platform (Render, Railway)

Autor
Helmuth 

📜 License
Free Demo.