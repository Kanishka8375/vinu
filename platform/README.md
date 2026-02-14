# Open-Source Long-Form Video Platform

Reference implementation for a **30-minute animated video platform** using:
- Next.js 14 + Tailwind + Shadcn-style UI patterns
- FastAPI orchestration + Celery workers
- ComfyUI API/WebSocket generation
- PostgreSQL + Redis
- S3 artifact storage

## Long-duration strategy

The pipeline does not attempt 30 minutes in one render. It uses:

`Script -> Scenes -> Shots -> Clips (2-4s) -> Stitch`

1. Generate clip A from prompt + seed + character consistency controls.
2. Extract final frame from clip A.
3. Feed that frame into clip B (`previous_frame`) for continuity.
4. Repeat for all clips in all shots/scenes.
5. Concatenate clips and mix voiceover/music with ffmpeg.

## Character consistency controls

- Inject **IP-Adapter reference image** for every clip.
- Inject **Character LoRA** (same LoRA and strength across project).
- Optional post-face restoration nodes can be added in the ComfyUI workflow.

## Local runbook

### 1) Infrastructure
```bash
cd platform
docker compose up -d
```

### 2) Backend API + Worker
```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# Terminal A
PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Terminal B
PYTHONPATH=. celery -A app.workers.celery_app:celery_app worker --loglevel=info
```

### 3) Frontend
```bash
cd ../frontend
npm install
npm run dev
```


### One-command launcher (Ubuntu)
```bash
cd platform
./scripts/run_local_ubuntu.sh up
./scripts/run_local_ubuntu.sh status
./scripts/run_local_ubuntu.sh logs
./scripts/run_local_ubuntu.sh down
```

What it does:
- starts Postgres + Redis with Docker Compose
- prepares backend `.venv` and installs `requirements.txt`
- starts FastAPI (`:8000`), Celery worker, and Next.js dev server (`:3000`)
- writes logs to `platform/.runlogs/`

### 4) Environment variables
```bash
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/vinu"
export REDIS_URL="redis://localhost:6379/0"
export COMFY_API_URL="http://localhost:8188"
export COMFY_WS_URL="ws://localhost:8188/ws"
export COMFY_WORKFLOW_JSON="/absolute/path/workflow_api.json"
export S3_BUCKET="your-bucket"
export AWS_REGION="us-east-1"
export COMFY_OUTPUT_DIR="/absolute/path/comfy/output"
export VIDEO_OUTPUT_DIR="/tmp/vinu-artifacts"
export OLLAMA_URL="http://localhost:11434"
export OLLAMA_MODEL="llama3"
```

## API smoke tests

Generate a 300-prompt plan:
```bash
curl -X POST http://localhost:8000/api/prompts/generate \
  -H 'Content-Type: application/json' \
  -d '{"story":"A cyberpunk detective story about a robot named X-7."}'
```

Queue a scene render:
```bash
curl -X POST http://localhost:8000/api/render/scene \
  -H 'Content-Type: application/json' \
  -d '{
    "project_id":"demo",
    "scene_id":"scene-1",
    "clips":[{"project_id":"demo","scene_id":"scene-1","shot_number":1,"clip_number":1,"prompt":"X-7 enters neon alley","seed":42,"model_name":"hunyuan_video","duration_sec":4,"fps":14,"character_ref":"/tmp/x7.png","lora_name":"x7.safetensors"}],
    "voiceover_path":"/tmp/voice.wav",
    "music_path":"/tmp/music.wav",
    "final_output_path":"/tmp/final.mp4"
  }'
```
