#!/usr/bin/env python3
"""Validate the deterministic Codex v2 pet atlas contract."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from PIL import Image

CELL_W, CELL_H = 192, 208
COLS, ROWS = 8, 11
EXPECTED_USED = [7, 8, 8, 4, 5, 8, 6, 6, 6, 8, 8]


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("atlas", type=Path)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--json-out", type=Path)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    errors: list[str] = []
    warnings: list[str] = []

    image = Image.open(args.atlas).convert("RGBA")
    if image.size != (COLS * CELL_W, ROWS * CELL_H):
        errors.append(f"expected 1536x2288, got {image.width}x{image.height}")

    transparent_rgb_residue = 0
    for r, expected in enumerate(EXPECTED_USED):
        for c in range(COLS):
            cell = image.crop((c * CELL_W, r * CELL_H, (c + 1) * CELL_W, (r + 1) * CELL_H))
            pixels = list(cell.getdata())
            visible = sum(1 for px in pixels if px[3] > 0)
            transparent_rgb_residue += sum(1 for px in pixels if px[3] == 0 and px[:3] != (0, 0, 0))
            if c < expected and visible == 0:
                errors.append(f"required cell r{r}c{c} is empty")
            if c >= expected and visible != 0:
                errors.append(f"unused cell r{r}c{c} is not transparent")

    if transparent_rgb_residue:
        errors.append(f"{transparent_rgb_residue} transparent pixels retain non-zero RGB")

    manifest_data = None
    if args.manifest:
        try:
            manifest_data = json.loads(args.manifest.read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"manifest cannot be parsed: {exc}")
        if manifest_data:
            if manifest_data.get("spriteVersionNumber") != 2:
                errors.append("manifest spriteVersionNumber must be 2")
            if not manifest_data.get("id"):
                errors.append("manifest id is required")
            if manifest_data.get("spritesheetPath") != args.atlas.name:
                warnings.append("manifest spritesheetPath differs from validated filename")

    report = {
        "ok": not errors,
        "file": str(args.atlas.resolve()),
        "width": image.width,
        "height": image.height,
        "columns": COLS,
        "rows": ROWS,
        "spriteVersionNumber": 2,
        "transparentRgbResiduePixels": transparent_rgb_residue,
        "errors": errors,
        "warnings": warnings,
    }
    rendered = json.dumps(report, ensure_ascii=False, indent=2)
    print(rendered)
    if args.json_out:
        args.json_out.write_text(rendered + "\n", encoding="utf-8")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
