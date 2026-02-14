import os
import subprocess
from typing import List, Optional


def stitch_video(clips: List[str], output_path: str, voiceover_path: Optional[str] = None, music_path: Optional[str] = None) -> str:
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    concat_file = f"{output_path}.txt"
    with open(concat_file, "w", encoding="utf-8") as f:
        for clip in clips:
            f.write(f"file '{os.path.abspath(clip)}'\n")

    temp_video = f"{output_path}.video.mp4"
    subprocess.run([
        "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", concat_file,
        "-c", "copy", temp_video,
    ], check=True, capture_output=True)

    if voiceover_path or music_path:
        inputs = ["-i", temp_video]
        if voiceover_path:
            inputs += ["-i", voiceover_path]
        if music_path:
            inputs += ["-i", music_path]

        filter_parts = []
        if voiceover_path and music_path:
            filter_parts.append("[1:a]volume=1.0[vo]")
            filter_parts.append("[2:a]volume=0.25[bg]")
            filter_parts.append("[vo][bg]amix=inputs=2:duration=longest[aout]")
            map_audio = ["-map", "0:v", "-map", "[aout]"]
        elif voiceover_path:
            map_audio = ["-map", "0:v", "-map", "1:a"]
        else:
            map_audio = ["-map", "0:v", "-map", "1:a"]

        cmd = ["ffmpeg", "-y", *inputs]
        if filter_parts:
            cmd += ["-filter_complex", ";".join(filter_parts)]
        cmd += [*map_audio, "-c:v", "copy", "-shortest", output_path]
        subprocess.run(cmd, check=True, capture_output=True)
    else:
        os.replace(temp_video, output_path)

    return output_path
