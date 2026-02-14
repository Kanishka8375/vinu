import json
from typing import List

import requests


class ScriptPromptBuilder:
    PROTAGONIST = "X-7 is a chrome-plated humanoid robot with cyan optic eyes, trench coat, and etched serial markings."

    def __init__(self, ollama_url: str, model: str):
        self.ollama_url = ollama_url.rstrip("/")
        self.model = model

    def build_300_prompts(self, story: str) -> List[str]:
        system = (
            "You are a storyboard generator. Return valid JSON only: "
            "{\"prompts\": [ ... exactly 300 strings ... ]}. "
            "Each prompt must include camera angle, lighting, action, and protagonist description."
        )
        user = (
            f"Story: {story}\n"
            f"Protagonist description to append to every prompt: {self.PROTAGONIST}\n"
            "Generate exactly 300 distinct cinematic prompts."
        )
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            "stream": False,
            "format": "json",
        }
        r = requests.post(f"{self.ollama_url}/api/chat", json=payload, timeout=120)
        r.raise_for_status()
        content = r.json()["message"]["content"]
        data = json.loads(content)

        prompts = data.get("prompts", [])
        prompts = [self._enforce_protagonist(p) for p in prompts][:300]
        if len(prompts) < 300:
            prompts.extend([self._enforce_protagonist(f"Cinematic filler beat {i+1}.") for i in range(300 - len(prompts))])
        return prompts

    def _enforce_protagonist(self, prompt: str) -> str:
        if self.PROTAGONIST in prompt:
            return prompt
        return f"{prompt.strip()} {self.PROTAGONIST}".strip()
