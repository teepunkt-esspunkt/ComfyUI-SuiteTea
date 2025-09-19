import os
import comfy.model_management as mm
import comfy.sd
import folder_paths


class Tea_ImageCheckpointFromPath:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "ckpt_path": ("STRING", {
                    "multiline": False,
                    "tooltip": "Full path to a .safetensors/.ckpt file."
                }),
            },
            "optional":{
                "ckpt_name": (
                    folder_paths.get_filename_list("checkpoints"),
                    {"tooltip": "Pick a checkpoint from models/checkpoints."}
                ),
                "prefer_dropdown": ("BOOLEAN", {
                    "default": False,
                    "tooltip": "If ON, load from dropdown instead of path."
                }),
            }
        }

    RETURN_TYPES = ("MODEL", "CLIP", "VAE", "CLIP_VISION")
    RETURN_NAMES = ("model", "clip", "vae", "clip_vision")
    FUNCTION = "load"
    CATEGORY = "SuiteTea/Loaders"

    def load(self, ckpt_path, ckpt_name=None, prefer_dropdown=False):
        # Use dropdown if explicitly requested OR if no path was provided
        if (prefer_dropdown and ckpt_name) or ((not ckpt_path) and ckpt_name):
            ckpt_path = folder_paths.get_full_path_or_raise("checkpoints", ckpt_name)

        if not ckpt_path or not os.path.isfile(ckpt_path):
            raise FileNotFoundError(f"Checkpoint not found: {ckpt_path}")

        mm.unload_all_models()

        out = comfy.sd.load_checkpoint_guess_config(
            ckpt_path,
            output_vae=True,
            output_clip=True,
            embedding_directory=folder_paths.get_folder_paths("embeddings"),
        )

        if len(out) == 4:
            model, clip, vae, clip_vision = out
        elif len(out) == 3:
            model, clip, vae = out # type: ignore
            clip_vision = None
        else:
            raise RuntimeError(f"Unexpected return length from load_checkpoint_guess_config: {len(out)}")

        return (model, clip, vae, clip_vision)