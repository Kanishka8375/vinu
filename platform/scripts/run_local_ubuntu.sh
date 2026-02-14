#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
BACKEND_DIR="$ROOT_DIR/backend"
FRONTEND_DIR="$ROOT_DIR/frontend"
LOG_DIR="$ROOT_DIR/.runlogs"
mkdir -p "$LOG_DIR"

export DATABASE_URL="${DATABASE_URL:-postgresql://postgres:postgres@localhost:5432/vinu}"
export REDIS_URL="${REDIS_URL:-redis://localhost:6379/0}"
export COMFY_API_URL="${COMFY_API_URL:-http://localhost:8188}"
export COMFY_WS_URL="${COMFY_WS_URL:-ws://localhost:8188/ws}"
export COMFY_WORKFLOW_JSON="${COMFY_WORKFLOW_JSON:-$ROOT_DIR/workflow_api.json}"
export COMFY_OUTPUT_DIR="${COMFY_OUTPUT_DIR:-/tmp/comfyui/output}"
export VIDEO_OUTPUT_DIR="${VIDEO_OUTPUT_DIR:-/tmp/vinu-artifacts}"
export OLLAMA_URL="${OLLAMA_URL:-http://localhost:11434}"
export OLLAMA_MODEL="${OLLAMA_MODEL:-llama3}"

usage() {
  cat <<USAGE
Usage: $(basename "$0") [up|down|status|logs]

Commands:
  up      Start infra + backend API + celery worker + frontend dev server
  down    Stop local processes started by this script and docker infra
  status  Show service status and important health checks
  logs    Tail runtime logs (api,worker,frontend)
USAGE
}

start_infra() {
  echo "[1/5] Starting Postgres + Redis via docker compose..."
  (cd "$ROOT_DIR" && docker compose up -d)
}

setup_backend_venv() {
  echo "[2/5] Preparing backend virtual environment..."
  if [[ ! -d "$BACKEND_DIR/.venv" ]]; then
    python3 -m venv "$BACKEND_DIR/.venv"
  fi
  source "$BACKEND_DIR/.venv/bin/activate"
  pip install -r "$BACKEND_DIR/requirements.txt" >/dev/null
  deactivate
}

start_api() {
  echo "[3/5] Starting FastAPI on :8000 ..."
  source "$BACKEND_DIR/.venv/bin/activate"
  (
    cd "$BACKEND_DIR"
    PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
  ) >"$LOG_DIR/api.log" 2>&1 &
  echo $! > "$LOG_DIR/api.pid"
  deactivate
}

start_worker() {
  echo "[4/5] Starting Celery worker ..."
  source "$BACKEND_DIR/.venv/bin/activate"
  (
    cd "$BACKEND_DIR"
    PYTHONPATH=. celery -A app.workers.celery_app:celery_app worker --loglevel=info
  ) >"$LOG_DIR/worker.log" 2>&1 &
  echo $! > "$LOG_DIR/worker.pid"
  deactivate
}

start_frontend() {
  echo "[5/5] Starting Next.js frontend on :3000 ..."
  if [[ ! -d "$FRONTEND_DIR/node_modules" ]]; then
    (cd "$FRONTEND_DIR" && npm install)
  fi
  (
    cd "$FRONTEND_DIR"
    npm run dev
  ) >"$LOG_DIR/frontend.log" 2>&1 &
  echo $! > "$LOG_DIR/frontend.pid"
}

stop_pid_file() {
  local pid_file="$1"
  if [[ -f "$pid_file" ]]; then
    local pid
    pid="$(cat "$pid_file")"
    if kill -0 "$pid" 2>/dev/null; then
      kill "$pid"
    fi
    rm -f "$pid_file"
  fi
}

do_status() {
  echo "== Docker services =="
  (cd "$ROOT_DIR" && docker compose ps)
  echo
  echo "== HTTP checks =="
  curl -fsS http://127.0.0.1:8000/health && echo
  curl -I -sS http://127.0.0.1:3000 | head -n 1
}

do_logs() {
  tail -n 50 -f "$LOG_DIR/api.log" "$LOG_DIR/worker.log" "$LOG_DIR/frontend.log"
}

cmd="${1:-up}"
case "$cmd" in
  up)
    start_infra
    setup_backend_venv
    start_api
    start_worker
    start_frontend
    echo
    echo "Started. Run: $(basename "$0") status"
    echo "Logs are in: $LOG_DIR"
    ;;
  down)
    stop_pid_file "$LOG_DIR/frontend.pid"
    stop_pid_file "$LOG_DIR/worker.pid"
    stop_pid_file "$LOG_DIR/api.pid"
    (cd "$ROOT_DIR" && docker compose down)
    echo "Stopped local stack."
    ;;
  status)
    do_status
    ;;
  logs)
    do_logs
    ;;
  *)
    usage
    exit 1
    ;;
esac
