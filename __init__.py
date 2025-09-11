# __init__.py (repo root)
from .suitetea.save_and_reload_image import Tea_SaveAndReloadImage
from .suitetea.checkpoint_from_path import Tea_CheckpointFromPath

NODE_CLASS_MAPPINGS = {
    "Tea_SaveAndReloadImage": Tea_SaveAndReloadImage,
    "Tea_CheckpointFromPath": Tea_CheckpointFromPath
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Tea_SaveAndReloadImage": "Tea: Save & Reload Image",
    "Tea_CheckpointFromPath": "Tea: Load Checkpoints from path"
}
