#!/usr/bin/env python3
"""Normalize every populated sprite cell into a Codex overlay-safe display box."""

from __future__ import annotations

import argparse
from pathlib import Path
from PIL import Image

CELL_W, CELL_H = 192, 208
SAFE_LEFT, SAFE_RIGHT = 18, 174
SAFE_TOP, SAFE_BOTTOM = 18, 184


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    atlas = Image.open(args.input).convert("RGBA")
    if atlas.size != (1536, 2288):
        raise SystemExit(f"expected 1536x2288 v2 atlas, got {atlas.width}x{atlas.height}")

    result = Image.new("RGBA", atlas.size, (0, 0, 0, 0))
    max_w, max_h = SAFE_RIGHT - SAFE_LEFT, SAFE_BOTTOM - SAFE_TOP

    for row in range(11):
        for col in range(8):
            cell = atlas.crop((col * CELL_W, row * CELL_H, (col + 1) * CELL_W, (row + 1) * CELL_H))
            bbox = cell.getchannel("A").getbbox()
            if bbox is None:
                continue
            sprite = cell.crop(bbox)
            scale = min(1.0, max_w / sprite.width, max_h / sprite.height)
            size = (max(1, round(sprite.width * scale)), max(1, round(sprite.height * scale)))
            if size != sprite.size:
                sprite = sprite.resize(size, Image.Resampling.LANCZOS)
            target = Image.new("RGBA", (CELL_W, CELL_H), (0, 0, 0, 0))
            target.alpha_composite(sprite, ((CELL_W - sprite.width) // 2, SAFE_BOTTOM - sprite.height))
            result.alpha_composite(target, (col * CELL_W, row * CELL_H))

    result.putdata([px if px[3] else (0, 0, 0, 0) for px in result.getdata()])
    args.output.parent.mkdir(parents=True, exist_ok=True)
    result.save(args.output, "WEBP", lossless=True, method=6, exact=True)
    print(args.output.resolve())


if __name__ == "__main__":
    main()

