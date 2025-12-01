from __future__ import annotations

import argparse
import shutil
from pathlib import Path


def package_viewer(
    glb_path: Path, output_dir: Path, dist_dir: Path, model_name: str = "generated.glb"
) -> Path:
    """
    Copy the built viewer (dist) to output_dir and drop the GLB into models/.
    Returns the final GLB path inside the packaged directory.
    """
    glb_path = glb_path.resolve()
    if not glb_path.exists():
        raise FileNotFoundError(f"GLB not found: {glb_path}")

    dist_dir = dist_dir.resolve()
    if not dist_dir.exists():
        raise FileNotFoundError(
            f"Viewer build not found: {dist_dir}. Run `npm run build` first."
        )

    output_dir = output_dir.resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"[package] Copy viewer assets from {dist_dir} -> {output_dir}")
    # copytree with dirs_exist_ok keeps hashed assets intact and allows reuse
    shutil.copytree(dist_dir, output_dir, dirs_exist_ok=True)

    target_glb = output_dir / "models" / model_name
    target_glb.parent.mkdir(parents=True, exist_ok=True)
    print(f"[package] Copy model -> {target_glb}")
    shutil.copy2(glb_path, target_glb)

    # Add a small helper file to remind how to open the packaged viewer.
    hint = output_dir / "viewer-url.txt"
    hint.write_text(
        "Open index.html with query: index.html?model=./models/"
        f"{model_name}\n"
        "Example (python): python -m http.server 8000\n"
        f"Then open http://localhost:8000/index.html?model=./models/{model_name}\n",
        encoding="utf-8",
    )

    return target_glb


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Package the built Vite viewer with a reconstructed GLB for easy sharing."
    )
    parser.add_argument("--glb", required=True, help="Path to the GLB to publish.")
    parser.add_argument(
        "--output",
        required=True,
        help="Target directory for the packaged viewer (e.g., reconstruction/outputs/run-001/web).",
    )
    parser.add_argument(
        "--dist",
        default="dist",
        help="Path to the built viewer assets (default: dist). Run `npm run build` first.",
    )
    parser.add_argument(
        "--model-name",
        default="generated.glb",
        help="Filename to use under models/ inside the packaged folder.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package_viewer(
        glb_path=Path(args.glb),
        output_dir=Path(args.output),
        dist_dir=Path(args.dist),
        model_name=args.model_name,
    )


if __name__ == "__main__":
    main()
