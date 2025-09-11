# ComfyUI-SuiteTea

Some good ComfyUI nodes for bad reasons.

## Install
- **ComfyUI Manager → Install from URL** →  
  https://github.com/teepunkt-esspunkt/ComfyUI-SuiteTea.git
- Or manually:  
  git clone https://github.com/teepunkt-esspunkt/ComfyUI-SuiteTea.git  
  into your `ComfyUI/custom_nodes/` folder.

---

## Nodes

### Tea: Save & Reload Image (category: SuiteTea / IO)

A utility node to save **VRAM** on of older GPU's
Some workflows pass images directly from one model to another → this can cause *out-of-memory* (OOM) errors on the first run.  
This node saves the IMAGE to disk and reloads it immediately, forcing upstream tensors to unload.

**Inputs**
- `image` (IMAGE)  
- `temp_folder` (default `output/temp`)  
- `filename` (default `bgstrip.png`)  
- `also_save_perm` (BOOLEAN, default `false`)  
- `perm_folder` (default `output/saved`)  

**Output**
- `reloaded_image` (BHWC float, shape 1×H×W×3)

**Usage**
Preprocessor → Tea: Save & Reload Image → Sampler.reference_image

---

### Tea: CheckpointLoader (category: SuiteTea / IO)

This Node is created to help run a python script run the same workflow with different models
A string-based checkpoint loader to work with external Python batch scripts.
Lets you loop the same workflow across multiple models without clicking through the dropdown.

**Inputs**
- `ckpt_path` (STRING, full path to .safetensors or .ckpt)  

**Usage** (model loop workflow)
1. Create a suiteTea_local.json in suitetea/scripts/ with your private model folder path: ```JSON { "MODELS_DIR": "C:/your/full/path/to/checkpoints" }```
2. Run discover_models_flat.py → generates models_list.txt.
3. Build a workflow modelloop.json using Tea: CheckpointLoader instead of the dropdown loader.
4. Run run_all_models.py → will iterate through all models in models_list.txt using the same workflow.

---

*(More nodes will be added here as SuiteTea grows.)*

## License
MIT
