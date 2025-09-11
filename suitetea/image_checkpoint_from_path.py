import os
import comfy.model_management as mm
import comfy.sd

class Tea_ImageCheckpointFromPath:
    @classmethod
    def INPUT_TYPES(cls):
        return {"required": {"ckpt_path": ("STRING", {"multiline": False})}}

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "CLIP_VISION")
    RETURN_NAMES = ("model", "clip", "vae", "clip_vision")
    FUNCTION = "load"
    CATEGORY = "SuiteTea/Loaders"

    def load(self, ckpt_path):
        if not os.path.isfile(ckpt_path):
            raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")

        mm.unload_all_models()

        # Robust across versions that return 3 or 4 values
        try:
            model, clip, vae, clip_vision = comfy.sd.load_checkpoint_guess_config(
                ckpt_path, output_vae=True, output_clip=True
            )
        except ValueError:
            model, clip, vae = comfy.sd.load_checkpoint_guess_config( # type: ignore
                ckpt_path, output_vae=True, output_clip=True
            )
            clip_vision = None

        return (model, clip, vae, clip_vision)