import copy
import shutil
import json
import os
import subprocess
from typing import List, Optional

from app.schemas import ClipRequest
from app.services.comfyui_client import ComfyUIClient


class VideoPipeline:
    def __init__(self, comfy_client: ComfyUIClient, workflow_path: str, comfy_output_dir: str):
        self.comfy_client = comfy_client
        self.workflow_path = workflow_path
        self.comfy_output_dir = comfy_output_dir

    def _load_workflow(self) -> dict:
        with open(self.workflow_path, "r", encoding="utf-8") as f:
            return json.load(f)

    def _inject_controls(self, workflow: dict, clip: ClipRequest, previous_frame: Optional[str]) -> dict:
        wf = copy.deepcopy(workflow)
        for node in wf.values():
            inputs = node.get("inputs", {})
            if "text" in inputs:
                inputs["text"] = clip.prompt
            if "seed" in inputs:
                inputs["seed"] = clip.seed
            if "steps" in inputs and clip.model_name.lower().startswith("hunyuan"):
                inputs["steps"] = max(25, inputs.get("steps", 30))
            if clip.character_ref and "image" in inputs:
                inputs["image"] = clip.character_ref
            if clip.lora_name and "lora_name" in inputs:
                inputs["lora_name"] = clip.lora_name
                if "strength_model" in inputs:
                    inputs["strength_model"] = clip.lora_strength
            if previous_frame and "init_image" in inputs:
                inputs["init_image"] = previous_frame
        return wf

    def _extract_last_frame(self, video_path: str, out_frame: str) -> str:
        os.makedirs(os.path.dirname(out_frame), exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-sseof", "-0.1", "-i", video_path,
            "-update", "1", "-q:v", "2", out_frame,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return out_frame

    def _apply_rife_target_fps(self, in_video: str, out_video: str, target_fps: int = 30) -> str:
        cmd = [
            "ffmpeg", "-y", "-i", in_video,
            "-vf", f"minterpolate=fps={target_fps}:mi_mode=mci",
            "-c:v", "libx264", "-pix_fmt", "yuv420p", out_video,
        ]
        subprocess.run(cmd, check=True, capture_output=True)
        return out_video

    def render_scene(self, clips: List[ClipRequest], artifact_dir: str) -> List[str]:
        os.makedirs(artifact_dir, exist_ok=True)
        base_workflow = self._load_workflow()
        previous_frame = None
        outputs: List[str] = []

        for clip in clips:
            workflow = self._inject_controls(base_workflow, clip, previous_frame)
            prompt_id = self.comfy_client.queue_prompt(workflow)
            history = self.comfy_client.wait_for_completion(prompt_id)
            comfy_file = self.comfy_client.find_first_artifact(history, ext=".mp4")
            if not comfy_file:
                raise RuntimeError(f"No .mp4 output for prompt_id={prompt_id}")

            comfy_artifact_path = self.comfy_client.resolve_artifact_path(comfy_file, self.comfy_output_dir)
            if not os.path.exists(comfy_artifact_path):
                raise FileNotFoundError(
                    f"Comfy output not found: {comfy_artifact_path}. Set COMFY_OUTPUT_DIR to the mounted Comfy output path."
                )

            raw_clip = os.path.join(artifact_dir, f"raw_s{clip.shot_number}_c{clip.clip_number}.mp4")
            if os.path.abspath(comfy_artifact_path) != os.path.abspath(raw_clip):
                shutil.copy2(comfy_artifact_path, raw_clip)

            smooth_clip = os.path.join(artifact_dir, f"clip_s{clip.shot_number}_c{clip.clip_number}_30fps.mp4")
            self._apply_rife_target_fps(raw_clip, smooth_clip, target_fps=30)
            outputs.append(smooth_clip)

            frame_path = os.path.join(artifact_dir, f"lastframe_s{clip.shot_number}_c{clip.clip_number}.png")
            previous_frame = self._extract_last_frame(smooth_clip, frame_path)

        return outputs
