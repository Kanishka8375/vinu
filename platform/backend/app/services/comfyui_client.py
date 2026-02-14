import json
import os
import uuid
from typing import Any, Dict, Optional
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

import requests
from websocket import create_connection


class ComfyUIClient:
    def __init__(self, api_url: str, ws_url: str):
        self.api_url = api_url.rstrip("/")
        self.ws_url = ws_url
        self.client_id: Optional[str] = None

    def queue_prompt(self, workflow: Dict[str, Any]) -> str:
        self.client_id = str(uuid.uuid4())
        payload = {"prompt": workflow, "client_id": self.client_id}
        response = requests.post(f"{self.api_url}/prompt", json=payload, timeout=30)
        response.raise_for_status()
        return response.json()["prompt_id"]

    def wait_for_completion(self, prompt_id: str, timeout_sec: int = 600) -> Dict[str, Any]:
        ws = create_connection(self._ws_url_with_client_id(), timeout=timeout_sec)
        try:
            while True:
                message = ws.recv()
                if isinstance(message, bytes):
                    continue
                event = json.loads(message)
                if event.get("type") == "executing":
                    data = event.get("data", {})
                    if data.get("prompt_id") == prompt_id and data.get("node") is None:
                        return self.get_history(prompt_id)
        finally:
            ws.close()

    def get_history(self, prompt_id: str) -> Dict[str, Any]:
        response = requests.get(f"{self.api_url}/history/{prompt_id}", timeout=30)
        response.raise_for_status()
        return response.json().get(prompt_id, {})

    @staticmethod
    def find_first_artifact(history: Dict[str, Any], ext: str = ".mp4") -> Optional[str]:
        outputs = history.get("outputs", {})
        for node_result in outputs.values():
            for item in node_result.get("files", []) + node_result.get("images", []) + node_result.get("gifs", []):
                name = item.get("filename", "")
                if name.endswith(ext):
                    return name
        return None

    def _ws_url_with_client_id(self) -> str:
        parsed = urlparse(self.ws_url)
        query = dict(parse_qsl(parsed.query))
        if self.client_id:
            query["clientId"] = self.client_id
        new_query = urlencode(query)
        return urlunparse(parsed._replace(query=new_query))

    @staticmethod
    def resolve_artifact_path(filename: str, comfy_output_dir: str) -> str:
        safe_name = os.path.basename(filename)
        return os.path.join(comfy_output_dir, safe_name)
