#!/usr/bin/env python3
"""Remove the background from an image (or a folder of images)."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image
from rembg import new_session, remove
from tqdm import tqdm

SUPPORTED_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
MODELS = ["u2net", "u2netp", "u2net_human_seg", "isnet-general-use", "silueta"]


def remove_background(
    in_path: Path,
    out_path: Path,
    session,
    alpha_matting: bool,
) -> None:
    with Image.open(in_path) as img:
        result = remove(
            img,
            session=session,
            alpha_matting=alpha_matting,
            alpha_matting_foreground_threshold=240,
            alpha_matting_background_threshold=10,
            alpha_matting_erode_size=10,
        )
        result.save(out_path, format="PNG")


def default_output_for(in_path: Path) -> Path:
    return in_path.with_name(f"{in_path.stem}_nobg.png")


def iter_images(folder: Path):
    for p in sorted(folder.iterdir()):
        if p.is_file() and p.suffix.lower() in SUPPORTED_EXTS:
            yield p


def run(args: argparse.Namespace) -> int:
    in_path = Path(args.input).expanduser().resolve()
    if not in_path.exists():
        print(f"error: input not found: {in_path}", file=sys.stderr)
        return 2

    session = new_session(args.model)

    if in_path.is_file():
        out_path = (
            Path(args.output).expanduser().resolve()
            if args.output
            else default_output_for(in_path)
        )
        if out_path.suffix.lower() != ".png":
            out_path = out_path.with_suffix(".png")
        out_path.parent.mkdir(parents=True, exist_ok=True)
        remove_background(in_path, out_path, session, args.alpha_matting)
        print(f"wrote {out_path}")
        return 0

    # directory mode
    out_dir = (
        Path(args.output).expanduser().resolve()
        if args.output
        else in_path / "nobg"
    )
    out_dir.mkdir(parents=True, exist_ok=True)

    images = list(iter_images(in_path))
    if not images:
        print(f"error: no supported images in {in_path}", file=sys.stderr)
        return 2

    failed = 0
    for img_path in tqdm(images, desc="removing bg", unit="img"):
        out_path = out_dir / f"{img_path.stem}_nobg.png"
        try:
            remove_background(img_path, out_path, session, args.alpha_matting)
        except Exception as e:
            failed += 1
            tqdm.write(f"failed {img_path.name}: {e}")
    print(f"done. wrote {len(images) - failed} files to {out_dir}")
    return 1 if failed else 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description="Remove image backgrounds. Single file or batch a folder.",
    )
    p.add_argument("input", help="Path to an image file or a folder of images")
    p.add_argument(
        "-o",
        "--output",
        help="Output path (file for single input, folder for batch). "
        "Defaults to <input>_nobg.png next to the source.",
    )
    p.add_argument(
        "-m",
        "--model",
        choices=MODELS,
        default="u2net",
        help="Segmentation model (default: u2net). "
        "Use u2netp for speed, isnet-general-use for sharper edges, "
        "u2net_human_seg or silueta for people.",
    )
    p.add_argument(
        "--alpha-matting",
        action="store_true",
        help="Enable alpha matting for cleaner hair/fur edges (slower).",
    )
    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
