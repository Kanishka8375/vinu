from fastapi import APIRouter

from app.config import settings
from app.schemas import PromptRequest, PromptResponse, SceneRenderRequest
from app.services.script_prompt_builder import ScriptPromptBuilder
from app.workers.tasks import render_scene_task

router = APIRouter(prefix="/api")


@router.post("/prompts/generate", response_model=PromptResponse)
def generate_prompts(request: PromptRequest) -> PromptResponse:
    builder = ScriptPromptBuilder(settings.ollama_url, settings.ollama_model)
    prompts = builder.build_300_prompts(request.story)
    return PromptResponse(count=len(prompts), prompts=prompts)


@router.post("/render/scene")
def queue_scene_render(request: SceneRenderRequest):
    task = render_scene_task.delay(request.model_dump())
    return {"task_id": task.id, "status": "queued"}
