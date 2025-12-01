from __future__ import annotations

import argparse
from pathlib import Path
import subprocess


def run_cmd(cmd: list[str]) -> None:
    print(f"[cmd] {' '.join(cmd)}")
    subprocess.run(cmd, check=True)


def extract(video: Path, output: Path, fps: float, max_size: int) -> None:
    video = video.resolve()
    if not video.exists():
        raise FileNotFoundError(f"Video not found: {video}")

    output = output.resolve()
    output.mkdir(parents=True, exist_ok=True)

    pattern = output / "frame_%06d.jpg"
    vf = f"fps={fps},scale='if(gt(iw,ih),{max_size},-2)':'if(gt(ih,iw),{max_size},-2)'"
    run_cmd(
        [
            "ffmpeg",
            "-y",
            "-i",
            str(video),
            "-vf",
            vf,
            "-q:v",
            "2",
            str(pattern),
        ]
    )
    print(f"[done] Frames saved to {output}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Extract frames from video for reconstruction.")
    parser.add_argument("--video", required=True, help="Input video file.")
    parser.add_argument("--output", required=True, help="Directory to store frames.")
    parser.add_argument("--fps", type=float, default=2.0, help="Sampling fps (default: 2).")
    parser.add_argument(
        "--max-size",
        type=int,
        default=2048,
        help="Downscale longer edge to this size (default: 2048).",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    extract(Path(args.video), Path(args.output), fps=args.fps, max_size=args.max_size)


if __name__ == "__main__":
    main()
