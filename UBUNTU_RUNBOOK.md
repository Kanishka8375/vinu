# Ubuntu Local Run Guide (Next.js + FastAPI + Celery + Postgres + Redis)

This runbook explains how to start and debug this repository on Ubuntu.

## 1) Install prerequisites

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip ffmpeg curl git
```

Install Node.js 20:

```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
```

Install Docker + Compose plugin:

```bash
sudo apt install -y docker.io docker-compose-plugin
sudo usermod -aG docker $USER
newgrp docker
```

## 2) Start infrastructure

From your project `platform/` directory (or wherever your `docker-compose.yml` lives):

```bash
docker compose up -d
docker compose ps
```

Expected running services:
- `postgres` on `5432`
- `redis` on `6379`

## 3) Set up backend virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## 4) Run FastAPI API (Terminal A)

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## 5) Run Celery worker (Terminal B)

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. celery -A app.workers.celery_app:celery_app worker --loglevel=info
```

## 6) Run frontend (Terminal C)

```bash
cd frontend
npm install
npm run dev
```

Open: <http://localhost:3000>


## 6.1) Optional one-command start script (recommended)

From repo root:

```bash
cd /workspace/vinu/platform
./scripts/run_local_ubuntu.sh up
./scripts/run_local_ubuntu.sh status
```

Useful commands:

```bash
./scripts/run_local_ubuntu.sh logs
./scripts/run_local_ubuntu.sh down
```

This script automates infra start, backend venv setup, API/worker/frontend startup, and health checks.

## 7) Optional environment variables

Set these for ComfyUI and output control:

```bash
export COMFY_API_URL="http://localhost:8188"
export COMFY_WS_URL="ws://localhost:8188/ws"
export COMFY_WORKFLOW_JSON="/absolute/path/to/workflow_api.json"
export COMFY_OUTPUT_DIR="/absolute/path/to/comfy/output"
export VIDEO_OUTPUT_DIR="/absolute/path/to/artifacts"
```

## 8) Smoke tests

### Prompt generation

```bash
curl -X POST http://localhost:8000/api/prompts/generate \
  -H 'Content-Type: application/json' \
  -d '{"story":"A cyberpunk detective story about a robot named X-7."}'
```

### Scene render queue

```bash
curl -X POST http://localhost:8000/api/render/scene \
  -H 'Content-Type: application/json' \
  -d '{
    "project_id":"demo",
    "scene_id":"scene-1",
    "clips":[
      {
        "project_id":"demo",
        "scene_id":"scene-1",
        "shot_number":1,
        "clip_number":1,
        "prompt":"Low-angle shot, neon alley, X-7 scans evidence",
        "seed":42,
        "model_name":"hunyuan_video",
        "duration_sec":4,
        "fps":14,
        "character_ref":"/path/to/x7_ref.png",
        "lora_name":"x7_character_lora.safetensors"
      }
    ],
    "voiceover_path":"/path/to/voice.wav",
    "music_path":"/path/to/music.wav",
    "final_output_path":"/path/to/final_scene.mp4"
  }'
```

## 9) Common errors and quick fixes

- `docker: permission denied`  
  Run `sudo usermod -aG docker $USER`, then re-login.

- `ModuleNotFoundError: app`  
  Run from the backend folder and include `PYTHONPATH=.`.

- Ollama connection errors on `:11434`  
  Start Ollama and ensure your model (for example `llama3`) is available.

- ComfyUI connection errors on `:8188`  
  Start ComfyUI and verify `COMFY_API_URL` / `COMFY_WS_URL`.

- Frontend cannot call API  
  Confirm backend is running on `:8000` and CORS configuration permits your origin.
