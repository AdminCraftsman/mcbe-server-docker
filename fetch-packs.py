MODS_DIR = Path(os.environ.get("MODS_DIR", "/mods"))

def find_pack_files():
    return sorted(MODS_DIR.glob("*.mcaddon")) + sorted(MODS_DIR.glob("*.mcpack"))

def extract(archive_path: Path) -> Path:
    extracted = DATA_DIR / ".pack-staging" / archive_path.stem
    if extracted.exists():
        shutil.rmtree(extracted)
    try:
        with zipfile.ZipFile(archive_path) as zf:
            zf.extractall(extracted)
    except zipfile.BadZipFile as e:
        raise PackError(f"{archive_path.name} is not a valid zip/.mcaddon/.mcpack file: {e}") from e
    return extracted

def main():
    pack_files = find_pack_files()
    if not pack_files:
        print(f"No pack files found in {MODS_DIR}, skipping pack install.")
        return
    for pf in pack_files:
        print(f"[processing] {pf.name}")
        extracted_root = extract(pf)
        manifests = find_manifests(extracted_root)
        print(f"  found {len(manifests)} pack(s) in {pf.name}")
        for m in manifests:
            register_pack(m, pf.name)