# __init__.py (repo root)
from .suitetea.save_and_reload_image import Tea_SaveAndReloadImage
from .suitetea.image_checkpoint_from_path import Tea_ImageCheckpointFromPath
from .suitetea.save_and_reload_imageV2 import Tea_SaveAndReloadImageV2

NODE_CLASS_MAPPINGS = {
    "Tea_SaveAndReloadImage": Tea_SaveAndReloadImage,
    "Tea_ImageCheckpointFromPath": Tea_ImageCheckpointFromPath,
    "Tea_SaveAndReloadImageV2": Tea_SaveAndReloadImageV2,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "Tea_SaveAndReloadImage": "Tea: Save & Reload Image",
    "Tea_ImageCheckpointFromPath": "Tea: Load Image Checkpoints from path",
    "Tea_SaveAndReloadImageV2": "Tea: Save & Reload Image V2 (with picker)",
}
