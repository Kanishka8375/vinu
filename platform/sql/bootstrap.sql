CREATE TYPE project_status AS ENUM ('DRAFT','PLANNING','RENDERING','COMPLETED','FAILED');
CREATE TYPE generation_status AS ENUM ('QUEUED','RUNNING','SUCCEEDED','FAILED');

CREATE TABLE projects (
  id TEXT PRIMARY KEY,
  title TEXT NOT NULL,
  synopsis TEXT,
  protagonist TEXT NOT NULL,
  status project_status NOT NULL DEFAULT 'DRAFT',
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE scripts (
  id TEXT PRIMARY KEY,
  project_id TEXT UNIQUE NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  raw_text TEXT NOT NULL,
  prompt_plan JSONB,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE scenes (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  scene_number INTEGER NOT NULL,
  title TEXT,
  summary TEXT,
  target_seconds INTEGER,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (project_id, scene_number)
);

CREATE TABLE generations (
  id TEXT PRIMARY KEY,
  project_id TEXT NOT NULL REFERENCES projects(id) ON DELETE CASCADE,
  scene_id TEXT NOT NULL REFERENCES scenes(id) ON DELETE CASCADE,
  shot_number INTEGER NOT NULL,
  clip_number INTEGER NOT NULL,
  prompt TEXT NOT NULL,
  seed INTEGER NOT NULL,
  model_name TEXT NOT NULL,
  duration_sec INTEGER NOT NULL,
  fps INTEGER NOT NULL,
  status generation_status NOT NULL DEFAULT 'QUEUED',
  comfy_prompt_id TEXT,
  s3_video_key TEXT,
  s3_frame_key TEXT,
  error_message TEXT,
  created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE (scene_id, shot_number, clip_number)
);

CREATE INDEX idx_scenes_project_id ON scenes(project_id);
CREATE INDEX idx_generations_project_status ON generations(project_id, status);
CREATE INDEX idx_generations_scene_status ON generations(scene_id, status);
