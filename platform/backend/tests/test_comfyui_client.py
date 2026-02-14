import unittest

from app.services.comfyui_client import ComfyUIClient


class ComfyUIClientTests(unittest.TestCase):
    def test_ws_url_includes_client_id(self):
        client = ComfyUIClient("http://localhost:8188", "ws://localhost:8188/ws")
        client.client_id = "abc-123"
        self.assertEqual(client._ws_url_with_client_id(), "ws://localhost:8188/ws?clientId=abc-123")

    def test_resolve_artifact_path_is_sanitized(self):
        path = ComfyUIClient.resolve_artifact_path("../escape.mp4", "/tmp/comfy")
        self.assertEqual(path, "/tmp/comfy/escape.mp4")


if __name__ == "__main__":
    unittest.main()
