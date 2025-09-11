# ComfyUI-SuiteTea

Some good ComfyUI nodes for bad reasons 

## Install
- **ComfyUI Manager → Install from URL** →  
  https://github.com/teepunkt-esspunkt/ComfyUI-SuiteTea.git
- Or manually:  
  git clone https://github.com/teepunkt-esspunkt/ComfyUI-SuiteTea.git  
  into your `ComfyUI/custom_nodes/` folder.

---

## Nodes

### Tea: Save & Reload Image (category: SuiteTea / IO)

A utility node to save **VRAM** because of old GPU
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

TEXT

**Inputs**??
- `image` (IMAGE)  
- `temp_folder` (default `output/temp`)  
- `filename` (default `bgstrip.png`)  
- `also_save_perm` (BOOLEAN, default `false`)  
- `perm_folder` (default `output/saved`)  

**Output** //
- `reloaded_image` (BHWC float, shape 1×H×W×3)

**Usage** + script??
Preprocessor → Tea: Save & Reload Image → Sampler.reference_image

---

*(More nodes will be added here as SuiteTea grows.)*

## License
MIT
