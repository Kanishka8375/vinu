"use client";

import { useState } from "react";

export function Dashboard() {
  const [story, setStory] = useState("A cyberpunk detective story about a robot named X-7.");
  const [message, setMessage] = useState("");

  const generatePrompts = async () => {
    const res = await fetch("http://localhost:8000/api/prompts/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ story }),
    });
    const data = await res.json();
    setMessage(`Generated ${data.count} prompts.`);
  };

  const queueRender = async () => {
    const payload = {
      project_id: "demo",
      scene_id: "scene-1",
      clips: [{
        project_id: "demo",
        scene_id: "scene-1",
        shot_number: 1,
        clip_number: 1,
        prompt: "Wide shot, neon rain, X-7 enters frame.",
        seed: 42,
        model_name: "hunyuan_video",
        duration_sec: 4,
        fps: 14,
        character_ref: "/tmp/x7.png",
        lora_name: "x7.safetensors"
      }],
      final_output_path: "/tmp/final.mp4"
    };
    const res = await fetch("http://localhost:8000/api/render/scene", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });
    const data = await res.json();
    setMessage(`Render task queued: ${data.task_id}`);
  };

  return (
    <main className="mx-auto max-w-4xl p-8 space-y-6">
      <h1 className="text-3xl font-bold">Long-Form Video Generator</h1>
      <p className="text-slate-300">Scene → Shot → Clip orchestration with ComfyUI continuity chaining.</p>
      <textarea
        className="w-full rounded border border-slate-700 bg-slate-900 p-3"
        rows={5}
        value={story}
        onChange={(e) => setStory(e.target.value)}
      />
      <div className="flex gap-3">
        <button className="rounded bg-indigo-600 px-4 py-2" onClick={generatePrompts}>Generate 300 Prompts</button>
        <button className="rounded bg-emerald-600 px-4 py-2" onClick={queueRender}>Queue Scene Render</button>
      </div>
      {message && <div className="rounded bg-slate-800 p-3 text-sm">{message}</div>}
    </main>
  );
}
