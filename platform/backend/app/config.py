import os


class Settings:
    comfy_api_url = os.getenv("COMFY_API_URL", "http://localhost:8188")
    comfy_ws_url = os.getenv("COMFY_WS_URL", "ws://localhost:8188/ws")
    comfy_workflow_json = os.getenv("COMFY_WORKFLOW_JSON", "workflow_api.json")
    comfy_output_dir = os.getenv("COMFY_OUTPUT_DIR", "/tmp/comfyui/output")
    redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    ollama_url = os.getenv("OLLAMA_URL", "http://localhost:11434")
    ollama_model = os.getenv("OLLAMA_MODEL", "llama3")
    video_output_dir = os.getenv("VIDEO_OUTPUT_DIR", "/tmp/vinu-artifacts")


settings = Settings()
