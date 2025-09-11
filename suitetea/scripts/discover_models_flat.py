import json, pathlib

HERE = pathlib.Path(__file__).parent
CFG = HERE / "suiteTea_local.json"
OUTFILE = HERE / "models_list.txt"
ALLOWED_EXT = {".safetensors", ".ckpt"}

def get_models_dir():
    if CFG.exists():
        data = json.loads(CFG.read_text(encoding="utf-8"))
        return pathlib.Path(data["MODELS_DIR"])
    raise FileNotFoundError(
        f"No suiteTea_local.json found at {CFG}. Please create it with {{\"MODELS_DIR\": \"path/to/checkpoints\"}}"
    )

def discover_models_flat(models_dir: pathlib.Path):
    return sorted(
        [p for p in models_dir.glob("*") if p.is_file() and p.suffix.lower() in ALLOWED_EXT],
        key=lambda x: x.name.lower()
    )


def main():
    models_dir = get_models_dir()
    models = discover_models_flat(models_dir)

    if not models:
        print(f"No models found in {models_dir}")
        return

    OUTFILE.write_text("\n".join(str(p) for p in models), encoding="utf-8")
    print(f"Wrote {len(models)} models to {OUTFILE}")


if __name__ == "__main__":
    main()