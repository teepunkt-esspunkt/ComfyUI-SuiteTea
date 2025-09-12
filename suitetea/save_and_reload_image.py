# suitetea/save_and_reload_image.py
from pathlib import Path
import numpy as np
from PIL import Image
import torch

def _to_pil(image: torch.Tensor) -> Image.Image:
    """
    Accepts IMAGE as torch.Tensor in BHWC (preferred) or BCHW/CHW.
    Saves/reloads only the FIRST item if batch>1.
    """
    t = image
    if isinstance(t, list):
        t = t[0]
    if not isinstance(t, torch.Tensor):
        raise ValueError("Expected IMAGE tensor.")
    # pick first in batch if present
    if t.dim() == 4:
        # BHWC vs BCHW
        if t.shape[-1] in (3, 4):       # BHWC
            t = t[0]                    # HWC
        else:                           # BCHW
            t = t[0].permute(1, 2, 0)   # CHW -> HWC
    elif t.dim() == 3:
        if t.shape[0] in (1, 3, 4):     # CHW -> HWC
            t = t.permute(1, 2, 0)
    else:
        raise ValueError(f"Unsupported tensor shape: {t.shape}")

    arr = (t.clamp(0, 1).cpu().numpy() * 255.0).astype(np.uint8)
    if arr.ndim == 2:
        arr = np.stack([arr, arr, arr], axis=-1)
    if arr.shape[-1] == 4:
        arr = arr[:, :, :3]
    return Image.fromarray(arr, mode="RGB")

def _from_pil(pil: Image.Image) -> torch.Tensor:
    """Return IMAGE as [1,H,W,3] float32 0..1 (CPU)."""
    pil = pil.convert("RGB")
    arr = np.array(pil, dtype=np.uint8)
    t = torch.from_numpy(arr).float() / 255.0
    return t.unsqueeze(0)

class Tea_SaveAndReloadImage:
    """
    Saves the incoming IMAGE to disk and reloads it to break upstream tensor references.
    Note: operates on the FIRST image in the batch.
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "image": ("IMAGE",),
                "temp_folder": ("STRING", {"default": "output/temp", "multiline": False}),
                "filename": ("STRING", {"default": "bgstrip.png", "multiline": False}),
                "also_save_perm": ("BOOLEAN", {"default": False}),
                "perm_folder": ("STRING", {"default": "output/saved", "multiline": False}),
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("reloaded_image",)
    FUNCTION = "run"
    CATEGORY = "SuiteTea/IO"

    def run(self, image, temp_folder, filename, also_save_perm, perm_folder):
        temp_dir = Path(temp_folder)
        perm_dir = Path(perm_folder)
        temp_dir.mkdir(parents=True, exist_ok=True)
        if also_save_perm:
            perm_dir.mkdir(parents=True, exist_ok=True)

        # ensure .png extension
        p = Path(filename)
        if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp"):
            p = p.with_suffix(".png")

        pil = _to_pil(image)
        temp_path = temp_dir / p.name
        pil.save(temp_path)  # overwrite ok

        if also_save_perm:
            pil.save(perm_dir / p.name)

        # reload
        with Image.open(temp_path) as im:
            out = _from_pil(im)

        return (out,)
