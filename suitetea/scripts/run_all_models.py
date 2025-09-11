# run_all_models.py
# Usage: start ComfyUI, then run:  python run_all_models.py

from pathlib import Path
import json, time, requests, traceback

# --- you adjust these ---
COMFY      = "http://127.0.0.1:8188"
TEMPLATE   = "modelloop.json"  # your saved API-format workflow using Tea_CheckpointFromPath
MODELS_DIR = Path(r"")  # flat folder with models
MODELS_TXT = None  # e.g. "models_list.txt" (one path per line) or None to scan folder

ALLOWED_EXT = {".safetensors", ".ckpt"}


# 1) model list (flat)
def discover_models_flat():
    return sorted(
        [p for p in MODELS_DIR.glob("*") if p.is_file() and p.suffix.lower() in ALLOWED_EXT],
        key=lambda x: x.name.lower()
    )

# 2) template load + patch ckpt_path
def load_template(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def set_ckpt_path(prompt_json, model_path_str):
    """
    Finds Tea_CheckpointFromPath and sets its 'ckpt_path' input.
    Returns True if found & set.
    """
    nodes = prompt_json.get("nodes", {})
    found = False
    for _, node in nodes.items():
        if node.get("class_type") == "Tea_CheckpointFromPath":
            node.setdefault("inputs", {})["ckpt_path"] = model_path_str
            found = True
    return found


# 3) enqueue + wait
def enqueue(prompt_json):
    r = requests.post(f"{COMFY}/prompt", json={"prompt": prompt_json})
    r.raise_for_status()
    return r.json().get("prompt_id", "")

def wait_until_idle(poll_s=1.2):
    while True:
        q = requests.get(f"{COMFY}/queue").json()
        if q.get("pending", 0) == 0 and q.get("running", 0) == 0:
            return
        time.sleep(poll_s)


# 4) glue it together
def main():
    models = load_models_from_txt(MODELS_TXT) if MODELS_TXT else discover_models_flat()
    if not models:
        print("! no models found")
        return

    print(f"Found {len(models)} models.")
    tpl = load_template(TEMPLATE)

    # write a quick record of what we plan to run
    stamp = time.strftime("%Y%m%d-%H%M%S")
    Path(f"models_ran_{stamp}.txt").write_text(
        "\n".join(str(p) for p in models), encoding="utf-8"
    )

    for m in models:
        print(f"\n=== {m.name} ===")
        try:
            # deep copy via json roundtrip (simple & safe for this dict)
            prompt = json.loads(json.dumps(tpl))
            if not set_ckpt_path(prompt, str(m)):
                print("! Tea_CheckpointFromPath not found in template. Skipping.")
                continue
            pid = enqueue(prompt)
            print(f"queued prompt_id={pid}")
            wait_until_idle()
            print("✓ done")
        except requests.HTTPError as e:
            print(f"! HTTP error on {m}: {e}")
            traceback.print_exc()
        except Exception as e:
            print(f"! failed on {m}: {e}")
            traceback.print_exc()

if __name__ == "__main__":
    main()
