from typing import List, Optional
from pydantic import BaseModel, Field


class ClipRequest(BaseModel):
    project_id: str
    scene_id: str
    shot_number: int
    clip_number: int
    prompt: str
    seed: int = 42
    model_name: str = "hunyuan_video"
    duration_sec: int = 4
    fps: int = 14
    character_ref: Optional[str] = None
    lora_name: Optional[str] = None
    lora_strength: float = 0.8


class SceneRenderRequest(BaseModel):
    project_id: str
    scene_id: str
    clips: List[ClipRequest]
    voiceover_path: Optional[str] = None
    music_path: Optional[str] = None
    final_output_path: str


class PromptRequest(BaseModel):
    story: str = Field(..., min_length=10)


class PromptResponse(BaseModel):
    count: int
    prompts: List[str]
