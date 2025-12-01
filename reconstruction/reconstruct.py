from __future__ import annotations

import argparse
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.append(str(SCRIPT_DIR))

try:
    import open3d as o3d
except ImportError:
    o3d = None

from create_page import package_viewer


def run_cmd(cmd: list[str]) -> None:
    print(f"[cmd] {' '.join(map(str, cmd))}")
    subprocess.run(cmd, check=True)


def extract_frames_from_video(
    video_path: Path, frames_dir: Path, fps: float, max_size: int
) -> Path:
    """
    Use ffmpeg to extract frames at given fps and downscale the longer edge to max_size.
    """
    video_path = video_path.resolve()
    if not video_path.exists():
        raise FileNotFoundError(f"Video not found: {video_path}")

    frames_dir = frames_dir.resolve()
    frames_dir.mkdir(parents=True, exist_ok=True)

    pattern = frames_dir / "frame_%06d.jpg"
    vf = f"fps={fps},scale='if(gt(iw,ih),{max_size},-2)':'if(gt(ih,iw),{max_size},-2)'"
    cmd = [
        "ffmpeg",
        "-y",
        "-i",
        str(video_path),
        "-vf",
        vf,
        "-q:v",
        "2",
        str(pattern),
    ]
    run_cmd(cmd)
    return frames_dir


def colmap_pipeline(images: Path, workspace: Path, colmap_bin: str, reuse: bool) -> Path:
    images = images.resolve()
    if not images.exists():
        raise FileNotFoundError(f"Images folder not found: {images}")

    workspace = workspace.resolve()
    workspace.mkdir(parents=True, exist_ok=True)

    db_path = workspace / "database.db"
    sparse_dir = workspace / "sparse"
    dense_dir = workspace / "dense"
    sparse_dir.mkdir(parents=True, exist_ok=True)
    dense_dir.mkdir(parents=True, exist_ok=True)

    fused_path = dense_dir / "fused.ply"
    if reuse and fused_path.exists():
        print(f"[reuse] Found existing fused cloud, skip COLMAP: {fused_path}")
        return fused_path

    run_cmd(
        [
            colmap_bin,
            "feature_extractor",
            "--database_path",
            str(db_path),
            "--image_path",
            str(images),
        ]
    )

    run_cmd(
        [
            colmap_bin,
            "exhaustive_matcher",
            "--database_path",
            str(db_path),
        ]
    )

    run_cmd(
        [
            colmap_bin,
            "mapper",
            "--database_path",
            str(db_path),
            "--image_path",
            str(images),
            "--output_path",
            str(sparse_dir),
        ]
    )

    run_cmd(
        [
            colmap_bin,
            "image_undistorter",
            "--image_path",
            str(images),
            "--input_path",
            str(sparse_dir / "0"),
            "--output_path",
            str(dense_dir),
        ]
    )

    run_cmd(
        [
            colmap_bin,
            "patch_match_stereo",
            "--workspace_path",
            str(dense_dir),
            "--workspace_format",
            "COLMAP",
            "--PatchMatchStereo.geom_consistency",
            "true",
        ]
    )

    run_cmd(
        [
            colmap_bin,
            "stereo_fusion",
            "--workspace_path",
            str(dense_dir),
            "--workspace_format",
            "COLMAP",
            "--input_type",
            "geometric",
            "--output_path",
            str(fused_path),
        ]
    )

    print(f"[done] Dense point cloud: {fused_path}")
    return fused_path


def point_cloud_to_glb(
    fused_path: Path,
    output_glb: Path,
    poisson_depth: int,
    target_triangles: int,
) -> Path:
    if o3d is None:
        raise RuntimeError(
            "open3d is not installed. Run `pip install -r reconstruction/requirements.txt`."
        )

    fused_path = fused_path.resolve()
    if not fused_path.exists():
        raise FileNotFoundError(f"Missing dense point cloud: {fused_path}")

    print(f"[mesh] Load point cloud: {fused_path}")
    pcd = o3d.io.read_point_cloud(str(fused_path))
    if len(pcd.points) == 0:
        raise RuntimeError("Point cloud is empty; check COLMAP outputs and image quality.")

    # Simple denoising to reduce outliers
    pcd, _ = pcd.remove_statistical_outlier(nb_neighbors=30, std_ratio=2.0)

    print(f"[mesh] Poisson reconstruction (depth={poisson_depth})")
    mesh, _ = o3d.geometry.TriangleMesh.create_from_point_cloud_poisson(
        pcd, depth=poisson_depth
    )

    print(f"[mesh] Simplify to ~{target_triangles} triangles")
    mesh = mesh.simplify_quadric_decimation(target_number_of_triangles=target_triangles)
    mesh.remove_degenerate_triangles()
    mesh.remove_duplicated_triangles()
    mesh.remove_duplicated_vertices()
    mesh.remove_non_manifold_edges()
    mesh.compute_vertex_normals()

    # Normalize to unit cube for easier viewing in Three.js
    bbox = mesh.get_axis_aligned_bounding_box()
    extent = max(bbox.get_extent())
    if extent == 0:
        raise RuntimeError("Mesh extent is zero; cannot normalize.")
    mesh.translate(-mesh.get_center())
    mesh.scale(1.0 / extent, center=(0, 0, 0))

    output_glb = output_glb.resolve()
    output_glb.parent.mkdir(parents=True, exist_ok=True)
    print(f"[mesh] Write GLB -> {output_glb}")
    o3d.io.write_triangle_mesh(str(output_glb), mesh, write_triangle_uvs=False)
    return output_glb


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Run COLMAP + Open3D to reconstruct a GLB from photos or a video, "
            "optionally package a viewer page."
        )
    )
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--images", help="Folder with input photos.")
    source.add_argument("--video", help="Video file to sample frames from.")

    parser.add_argument(
        "--fps",
        type=float,
        default=2.0,
        help="When using --video, sample this many frames per second (default: 2).",
    )
    parser.add_argument(
        "--max-size",
        type=int,
        default=2048,
        help="When using --video, downscale longer edge to this size (default: 2048).",
    )
    parser.add_argument(
        "--workspace",
        help="Workspace folder for intermediate outputs.",
    )
    parser.add_argument(
        "--colmap-bin",
        default="colmap",
        help="COLMAP executable name or path (default: colmap).",
    )
    parser.add_argument(
        "--poisson-depth",
        type=int,
        default=10,
        help="Poisson reconstruction depth (higher = more detail, slower).",
    )
    parser.add_argument(
        "--target-triangles",
        type=int,
        default=50000,
        help="Target triangle count after simplification.",
    )
    parser.add_argument(
        "--glb-name",
        default="model.glb",
        help="Filename for the exported GLB under workspace/meshes/.",
    )
    parser.add_argument(
        "--reuse",
        action="store_true",
        help="Reuse existing dense/fused outputs if they already exist.",
    )
    parser.add_argument(
        "--export-public",
        action="store_true",
        help="Copy the GLB to public/models/generated.glb for immediate viewing in the app.",
    )
    parser.add_argument(
        "--page-output",
        help="Optional: package a static viewer page into this folder (uses dist build).",
    )
    parser.add_argument(
        "--dist-dir",
        default="dist",
        help="Path to the built viewer assets (default: dist). Run `npm run build` first.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    run_id = datetime.now().strftime("%Y%m%d-%H%M%S")
    workspace = Path(args.workspace or (SCRIPT_DIR / "outputs" / f"run-{run_id}")).resolve()

    if args.video:
        frames_dir = workspace / "frames"
        print(f"[extract] Sampling frames from video -> {frames_dir}")
        images_dir = extract_frames_from_video(
            video_path=Path(args.video),
            frames_dir=frames_dir,
            fps=args.fps,
            max_size=args.max_size,
        )
    else:
        images_dir = Path(args.images)

    fused = colmap_pipeline(
        images=images_dir,
        workspace=workspace,
        colmap_bin=args.colmap_bin,
        reuse=args.reuse,
    )

    glb_path = workspace / "meshes" / args.glb_name
    glb_path = point_cloud_to_glb(
        fused_path=fused,
        output_glb=glb_path,
        poisson_depth=args.poisson_depth,
        target_triangles=args.target_triangles,
    )

    if args.export_public:
        target = Path("public/models/generated.glb").resolve()
        target.parent.mkdir(parents=True, exist_ok=True)
        print(f"[export] Copy GLB -> {target}")
        shutil.copy2(glb_path, target)

    if args.page_output:
        package_viewer(
            glb_path=glb_path,
            output_dir=Path(args.page_output),
            dist_dir=Path(args.dist_dir),
            model_name=args.glb_name,
        )

    print("\n[summary]")
    print(f"workspace: {workspace}")
    print(f"glb: {glb_path}")
    if args.export_public:
        print("public viewer: public/models/generated.glb (open with ?model=/models/generated.glb)")
    if args.page_output:
        print(f"packaged viewer: {Path(args.page_output).resolve()}")


if __name__ == "__main__":
    main()
