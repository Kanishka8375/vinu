import os

from app.config import settings
from app.schemas import ClipRequest
from app.services.comfyui_client import ComfyUIClient
from app.services.video_pipeline import VideoPipeline
from app.utils.stitching import stitch_video
from app.workers.celery_app import celery_app


@celery_app.task(name="render_scene")
def render_scene_task(payload: dict) -> dict:
    comfy = ComfyUIClient(settings.comfy_api_url, settings.comfy_ws_url)
    pipeline = VideoPipeline(comfy, settings.comfy_workflow_json, settings.comfy_output_dir)

    clips = [ClipRequest(**clip) for clip in payload["clips"]]
    artifact_dir = os.path.join(settings.video_output_dir, payload["project_id"], payload["scene_id"])
    rendered = pipeline.render_scene(clips, artifact_dir)

    final_path = stitch_video(
        rendered,
        payload["final_output_path"],
        voiceover_path=payload.get("voiceover_path"),
        music_path=payload.get("music_path"),
    )
    return {"scene_id": payload["scene_id"], "output": final_path, "clips": rendered}
