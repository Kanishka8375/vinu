import json
import tempfile
import unittest
from pathlib import Path

from app.schemas import ClipRequest
from app.services.video_pipeline import VideoPipeline


class DummyClient:
    def queue_prompt(self, workflow):
        return "prompt-1"

    def wait_for_completion(self, prompt_id):
        return {"outputs": {"1": {"files": [{"filename": "clip.mp4"}]}}}

    def find_first_artifact(self, history, ext=".mp4"):
        return "clip.mp4"

    def resolve_artifact_path(self, filename, output_dir):
        return str(Path(output_dir) / filename)


class VideoPipelineTests(unittest.TestCase):
    def test_render_scene_raises_if_artifact_missing(self):
        with tempfile.TemporaryDirectory() as d:
            workflow_path = Path(d) / "wf.json"
            workflow_path.write_text(json.dumps({"1": {"inputs": {"text": "x"}}}))

            pipeline = VideoPipeline(DummyClient(), str(workflow_path), d)
            clip = ClipRequest(
                project_id="p1",
                scene_id="s1",
                shot_number=1,
                clip_number=1,
                prompt="x",
            )
            with self.assertRaises(FileNotFoundError):
                pipeline.render_scene([clip], str(Path(d) / "artifacts"))


if __name__ == "__main__":
    unittest.main()
