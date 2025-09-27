# suitetea/save_and_reload_image_v2.py
from pathlib import Path
import os
import numpy as np
import torch
from PIL import Image, ImageOps, ImageSequence
import folder_paths

def _to_pil(image: torch.Tensor) -> Image.Image:
    t = image[0] if isinstance(image, list) else image
    if not isinstance(t, torch.Tensor):
        raise ValueError("Expected IMAGE tensor.")
    if t.dim() == 4:
        t = t[0] if t.shape[-1] in (3, 4) else t[0].permute(1, 2, 0)
    elif t.dim() == 3 and t.shape[0] in (1, 3, 4):
        t = t.permute(1, 2, 0)
    arr = (t.clamp(0, 1).cpu().numpy() * 255.0).astype(np.uint8)
    if arr.ndim == 2: arr = np.stack([arr, arr, arr], -1)
    if arr.shape[-1] == 4: arr = arr[:, :, :3]
    return Image.fromarray(arr, "RGB")

def _from_pil(pil: Image.Image) -> torch.Tensor:
    pil = pil.convert("RGB")
    arr = np.array(pil, dtype=np.uint8)
    t = torch.from_numpy(arr).float() / 255.0
    return t.unsqueeze(0)  # [1,H,W,3]

class Tea_SaveAndReloadImage:
    """
    - If `image_in` (tensor) is provided: save→reload using ONLY `filename` for both temp & perm.
      (Detaches upstream tensors; perm copy optional; overwrites if exists.)
    - Else: use REQUIRED `image` picker (with Upload button + preview).
    """

    @classmethod
    def INPUT_TYPES(cls):
        input_dir = folder_paths.get_input_directory()
        try:
            files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        except FileNotFoundError:
            files = []
        files = folder_paths.filter_files_content_types(files, ["image"])
        files.sort()

        return {
            "required": {
                # picker must be named 'image' & be REQUIRED to get upload button + thumbnail
                "image": (files, {"image_upload": True}),
                "temp_folder": ("STRING", {"default": "output/temp"}),
                "filename": ("STRING", {"default": "Teafault.png"}),   # <- default now Teafault.png
                "also_save_perm": ("BOOLEAN", {"default": False}),
                "perm_folder": ("STRING", {"default": "output/saved"}),  # <- prefilled
            },
            "optional": {
                "image_in": ("IMAGE",),   # optional tensor input (triggers save→reload path)
            }
        }

    RETURN_TYPES = ("IMAGE",)
    RETURN_NAMES = ("reloaded_image",)
    FUNCTION = "run"
    CATEGORY = "SuiteTea/IO"

    def _load_from_picker(self, annotated_name: str):
        full = folder_paths.get_annotated_filepath(annotated_name)
        if not os.path.isfile(full):
            raise FileNotFoundError(f"Tea_SaveAndReloadImageV2: file not found → {full}")
        img = Image.open(full)
        # mimic stock loader: exif transpose + multi-frame, consistent size
        out = []
        w = h = None
        for i in ImageSequence.Iterator(img):
            i = ImageOps.exif_transpose(i)
            rgb = i.convert("RGB")
            if w is None: w, h = rgb.size
            if rgb.size != (w, h): continue
            out.append(_from_pil(rgb))
        img.close()
        return out[0] if out else _from_pil(Image.open(full))

    def run(self, image, temp_folder, filename, also_save_perm, perm_folder, image_in=None):
        # If a tensor is connected → save→reload (detach), using ONLY the provided `filename`
        if image_in is not None:
            temp_dir = Path(temp_folder); temp_dir.mkdir(parents=True, exist_ok=True)
            if also_save_perm:
                Path(perm_folder).mkdir(parents=True, exist_ok=True)

            # enforce extension on filename (default .png if missing/wrong)
            p = Path(filename)
            if p.suffix.lower() not in (".png", ".jpg", ".jpeg", ".webp", ".bmp"):
                p = p.with_suffix(".png")

            pil = _to_pil(image_in)

            # write temp (overwrite if exists)
            temp_path = temp_dir / p.name
            pil.save(temp_path)

            # optional permanent copy (overwrite if exists)
            if also_save_perm:
                pil.save(Path(perm_folder) / p.name)

            # reload from temp to return a detached CPU tensor
            with Image.open(temp_path) as im:
                out = _from_pil(im)
            return (out,)

        # Else: just load via picker (no saving)
        loaded = self._load_from_picker(image)
        return (loaded,)
