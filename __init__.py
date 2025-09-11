# __init__.py (repo root)
from .suitetea.save_and_reload_image import Tea_SaveAndReloadImage
from .suitetea.image_checkpoint_from_path import Tea_ImageCheckpointFromPath

NODE_CLASS_MAPPINGS = {
    "Tea_SaveAndReloadImage": Tea_SaveAndReloadImage,
    "Tea_ImageCheckpointFromPath": Tea_ImageCheckpointFromPath
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Tea_SaveAndReloadImage": "Tea: Save & Reload Image",
    "Tea_ImageCheckpointFromPath": "Tea: Load Image Checkpoints from path"
}
