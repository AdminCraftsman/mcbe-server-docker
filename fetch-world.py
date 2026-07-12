#!/usr/bin/env python3
"""
Install a .mcworld file from the local mods folder as the server's active world.
"""
import os
import shutil
import sys
import zipfile
from pathlib import Path

BEDROCK_DIR = Path(os.environ.get("BEDROCK_DIR", "/home/minecraft"))
MODS_DIR = Path(os.environ.get("MODS_DIR", f"{BEDROCK_DIR}/mods"))
DATA_DIR = Path(os.environ.get("DATA_DIR", f"{BEDROCK_DIR}/data"))
WORLD_NAME = os.environ.get("WORLD_NAME", "Bedrock level")
WORLD_DIR = BEDROCK_DIR / "worlds" / WORLD_NAME
BEHAVIOR_PACKS_DIR = BEDROCK_DIR / "behavior_packs"
RESOURCE_PACKS_DIR = BEDROCK_DIR / "resource_packs"
SERVER_PROPERTIES = BEDROCK_DIR / "server.properties"


class WorldError(Exception):
    """Raised for any world file that is missing, ambiguous, malformed, or fails to install."""


def find_world_file() -> Path | None:
    candidates = sorted(MODS_DIR.glob("*.mcworld"))
    if not candidates:
        return None

    explicit = os.environ.get("WORLD_FILE", "").strip()
    if explicit:
        match = MODS_DIR / explicit
        if not match.exists():
            raise WorldError(f"WORLD_FILE={explicit} not found in {MODS_DIR}")
        return match

    if len(candidates) > 1:
        raise WorldError(
            f"multiple .mcworld files found in {MODS_DIR} ({[c.name for c in candidates]}) — "
            f"set WORLD_FILE to pick one"
        )
    return candidates[0]


def extract_and_validate(archive_path: Path) -> Path:
    staging = DATA_DIR / ".world-staging"
    if staging.exists():
        shutil.rmtree(staging)

    try:
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(staging)
    except zipfile.BadZipFile as e:
        raise WorldError(f"{archive_path.name} is not a valid zip/.mcworld file: {e}") from e

    if not (staging / "level.dat").exists():
        raise WorldError(
            f"{archive_path.name} has no level.dat at its root — not a valid .mcworld "
            f"(found: {[p.name for p in staging.iterdir()]})"
        )
    return staging


def extract_packs(staging: Path, pack_type: str, target_dir: Path):
    packs_src = staging / pack_type
    if not packs_src.is_dir():
        return
    target_dir.mkdir(parents=True, exist_ok=True)
    for pack_folder in packs_src.iterdir():
        if not pack_folder.is_dir():
            continue
        dest = target_dir / pack_folder.name
        if dest.exists():
            shutil.rmtree(dest)
        shutil.move(str(pack_folder), str(dest))
        print(f"[installed {pack_type[:-1]}] {pack_folder.name}")
    shutil.rmtree(packs_src)


def install(staging: Path):
    extract_packs(staging, "behavior_packs", BEHAVIOR_PACKS_DIR)
    extract_packs(staging, "resource_packs", RESOURCE_PACKS_DIR)

    if WORLD_DIR.exists():
        print(f"[replacing existing world at {WORLD_DIR}]")
        shutil.rmtree(WORLD_DIR)
    WORLD_DIR.parent.mkdir(parents=True, exist_ok=True)
    shutil.move(str(staging), str(WORLD_DIR))


def set_level_name():
    if not SERVER_PROPERTIES.exists():
        raise WorldError(f"{SERVER_PROPERTIES} not found — cannot set level-name")
    lines = SERVER_PROPERTIES.read_text().splitlines()
    found = False
    for i, line in enumerate(lines):
        if line.startswith("level-name="):
            lines[i] = f"level-name={WORLD_NAME}"
            found = True
            break
    if not found:
        lines.append(f"level-name={WORLD_NAME}")
    SERVER_PROPERTIES.write_text("\n".join(lines) + "\n")
    print(f"[set level-name={WORLD_NAME} in server.properties]")


def main():
    world_file = find_world_file()
    if world_file is None:
        print(f"No .mcworld file found in {MODS_DIR}, skipping world install.")
        return

    print(f"[installing world] {world_file.name}")
    staging = extract_and_validate(world_file)
    install(staging)
    set_level_name()


if __name__ == "__main__":
    try:
        main()
    except WorldError as e:
        print(f"FATAL: {e}", file=sys.stderr)
        sys.exit(1)