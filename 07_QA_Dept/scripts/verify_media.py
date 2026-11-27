#!/usr/bin/env python3
"""
メディア品質数値監査スクリプト (07_QA_Dept)
- 動画/音声/画像の解像度・fps・尺・コーデック・容量・ラウドネス(LUFS/True Peak)をJSON出力
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path


def probe_media(target: Path, measure_loudness: bool = False) -> dict:
    info: dict = {
        "file": str(target),
        "exists": target.exists(),
        "size_bytes": target.stat().st_size if target.exists() else 0,
        "size_mb": round(target.stat().st_size / (1024 * 1024), 3) if target.exists() else 0.0,
    }
    if not target.exists():
        info["error"] = "File not found"
        return info

    ffprobe = shutil.which("ffprobe")
    if ffprobe:
        proc = subprocess.run(
            [ffprobe, "-v", "error", "-show_format", "-show_streams", "-of", "json", str(target)],
            capture_output=True,
            text=True,
        )
        if proc.returncode == 0:
            data = json.loads(proc.stdout)
            fmt = data.get("format", {})
            info["duration_sec"] = float(fmt.get("duration", 0) or 0)
            info["bit_rate"] = int(fmt.get("bit_rate", 0) or 0)
            streams = []
            for s in data.get("streams", []):
                entry = {
                    "type": s.get("codec_type"),
                    "codec": s.get("codec_name"),
                }
                if s.get("codec_type") == "video":
                    entry.update(
                        {
                            "width": s.get("width"),
                            "height": s.get("height"),
                            "pix_fmt": s.get("pix_fmt"),
                            "r_frame_rate": s.get("r_frame_rate"),
                        }
                    )
                elif s.get("codec_type") == "audio":
                    entry.update(
                        {
                            "sample_rate": s.get("sample_rate"),
                            "channels": s.get("channels"),
                        }
                    )
                streams.append(entry)
            info["streams"] = streams
        else:
            info["ffprobe_error"] = proc.stderr.strip()
    else:
        info["ffprobe_warning"] = "ffprobe not found in PATH"

    ffmpeg = shutil.which("ffmpeg")
    if measure_loudness and ffmpeg:
        proc = subprocess.run(
            [
                ffmpeg,
                "-hide_banner",
                "-nostats",
                "-i",
                str(target),
                "-filter_complex",
                "ebur128=peak=true",
                "-f",
                "null",
                "-",
            ],
            capture_output=True,
            text=True,
        )
        stderr = proc.stderr
        m_i = re.search(r"I:\s*(-?\d+(?:\.\d+)?)\s*LUFS", stderr)
        m_tp = re.search(r"Peak:\s*(-?\d+(?:\.\d+)?)\s*dBFS", stderr)
        info["loudness"] = {
            "integrated_lufs": float(m_i.group(1)) if m_i else None,
            "true_peak_dbfs": float(m_tp.group(1)) if m_tp else None,
        }

    return info


def main() -> int:
    parser = argparse.ArgumentParser(description="Probe media quality metrics as JSON")
    parser.add_argument("files", nargs="+", help="Target media files")
    parser.add_argument("--loudness", action="store_true", help="Measure integrated LUFS via ffmpeg ebur128")
    args = parser.parse_args()

    results = [probe_media(Path(f), measure_loudness=args.loudness) for f in args.files]
    print(json.dumps(results, ensure_ascii=False, indent=2))
    return 0 if all(r.get("exists") for r in results) else 1


if __name__ == "__main__":
    sys.exit(main())
