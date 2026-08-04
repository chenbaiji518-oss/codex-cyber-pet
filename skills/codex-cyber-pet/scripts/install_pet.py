#!/usr/bin/env python3
"""Install a validated custom pet and optionally select it in Codex config."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import shutil
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--pet-dir", type=Path, required=True)
    parser.add_argument("--codex-home", type=Path, default=Path.home() / ".codex")
    parser.add_argument("--select", action="store_true")
    return parser.parse_args()


def select_pet(config: Path, pet_id: str) -> None:
    text = config.read_text(encoding="utf-8") if config.exists() else ""
    value = f'custom:{pet_id}'
    section = re.search(r"(?ms)^\[desktop\]\n(.*?)(?=^\[|\Z)", text)
    if section:
        body = section.group(1)
        if re.search(r"(?m)^selected-avatar-id\s*=", body):
            new_body = re.sub(r'(?m)^selected-avatar-id\s*=.*$', f'selected-avatar-id = "{value}"', body)
        else:
            new_body = body + f'selected-avatar-id = "{value}"\n'
        text = text[: section.start(1)] + new_body + text[section.end(1) :]
    else:
        text = text.rstrip() + f'\n\n[desktop]\nselected-avatar-id = "{value}"\n'
    config.write_text(text, encoding="utf-8")


def main() -> None:
    args = parse_args()
    manifest_path = args.pet_dir / "pet.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    pet_id = manifest["id"]
    if manifest.get("spriteVersionNumber") != 2:
        raise SystemExit("pet.json must declare spriteVersionNumber 2")
    sheet = args.pet_dir / manifest.get("spritesheetPath", "spritesheet.webp")
    if not sheet.exists():
        raise SystemExit(f"missing spritesheet: {sheet}")

    destination = args.codex_home / "pets" / pet_id
    destination.parent.mkdir(parents=True, exist_ok=True)
    if destination.exists():
        stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
        backup = destination.with_name(f"{pet_id}.backup-{stamp}")
        shutil.move(destination, backup)
        print(f"backup={backup}")
    shutil.copytree(args.pet_dir, destination)
    if args.select:
        select_pet(args.codex_home / "config.toml", pet_id)
    print(f"installed={destination}")
    print("restart_required=true")


if __name__ == "__main__":
    main()

