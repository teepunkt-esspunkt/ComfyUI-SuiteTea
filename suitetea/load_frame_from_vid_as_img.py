# suitetea/load_frame_from_vid_as_img.py
import os
import io
import subprocess
from typing import Optional

import numpy as np
import torch
from PIL import Image
import folder_paths

# ---------- helpers ----------
def _resize_if_needed(img_t: torch.Tensor, max_side: int) -> torch.Tensor:
    if max_side <= 0:
        return img_t
    _, h, w, _ = img_t.shape
    m = max(h, w)
    if m <= max_side:
        return img_t
    scale = max_side / float(m)
    nh, nw = max(1, int(round(h * scale))), max(1, int(round(w * scale)))
    x = img_t.permute(0, 3, 1, 2)  # (1,3,H,W)
    x = torch.nn.functional.interpolate(x, size=(nh, nw), mode="area")
    return x.permute(0, 2, 3, 1)

def _png_bytes_to_image_tensor(png_bytes: bytes) -> torch.Tensor:
    img = Image.open(io.BytesIO(png_bytes)).convert("RGB")
    arr = np.array(img).astype(np.float32) / 255.0  # (H,W,3) in [0,1]
    arr = np.expand_dims(arr, 0)  # (1,H,W,3)
    return torch.from_numpy(arr)

def _ensure_parent(path: str):
    p = os.path.abspath(path)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p

def _save_tensor_to_png(img_t: torch.Tensor, path: str) -> str:
    img = (img_t[0].clamp(0.0, 1.0).numpy() * 255.0).astype(np.uint8)
    im = Image.fromarray(img, mode="RGB")
    path = _ensure_parent(path)
    im.save(path, format="PNG", optimize=True)
    return path

def _auto_save_name(video_path: str, mode: str, frame_index: int, time_sec: float) -> str:
    base = os.path.splitext(os.path.basename(video_path))[0]
    if mode == "first":
        tag = "first"
    elif mode == "last":
        tag = "last"
    elif mode == "index":
        tag = f"n{frame_index}"
    else:
        tag = f"t{int(round(time_sec * 1000))}ms"
    return os.path.join("output", "tea_frames", f"{base}_{tag}.png")

def _ffmpeg_bytes(cmd: list) -> Optional[bytes]:
    try:
        out = subprocess.check_output(cmd, stderr=subprocess.DEVNULL)
        return out if out and len(out) > 8 else None
    except Exception:
        return None

def _extract_with_ffmpeg(video_path: str, mode: str, frame_index: int, time_sec: float) -> Optional[bytes]:
    common = ["-hide_banner", "-loglevel", "error", "-frames:v", "1", "-f", "image2pipe", "-vcodec", "png", "pipe:1"]

    if mode == "first":
        cmd = ["ffmpeg", "-ss", "0", "-i", video_path] + common
        return _ffmpeg_bytes(cmd)
    if mode == "last":
        cmd = ["ffmpeg", "-sseof", "-0.05", "-i", video_path] + common
        return _ffmpeg_bytes(cmd)
    if mode == "time":
        t = max(0.0, float(time_sec))
        cmd = ["ffmpeg", "-ss", f"{t:.3f}", "-i", video_path] + common
        return _ffmpeg_bytes(cmd)
    if mode == "index":
        cmd = ["ffmpeg", "-i", video_path, "-vf", f"select='eq(n\\,{frame_index})',setpts=N/FRAME_RATE/TB"] + common
        return _ffmpeg_bytes(cmd)
    return None

def _extract_with_opencv(video_path: str, mode: str, frame_index: int, time_sec: float) -> Optional[bytes]:
    try:
        import cv2
    except Exception:
        return None

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        return None

    if mode == "first":
        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
    elif mode == "last":
        total = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) or 0
        if total > 0:
            cap.set(cv2.CAP_PROP_POS_FRAMES, total - 1)
    elif mode == "time":
        cap.set(cv2.CAP_PROP_POS_MSEC, max(0.0, float(time_sec)) * 1000.0)
    elif mode == "index":
        cap.set(cv2.CAP_PROP_POS_FRAMES, max(0, int(frame_index)))

    ok, frame = cap.read()
    cap.release()
    if not ok or frame is None:
        return None

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    ok, buf = cv2.imencode(".png", frame)
    if not ok:
        return None
    return buf.tobytes()

# ---------- node ----------
class Tea_LoadFrameFromVidAsImg:
    """
    Load a frame from a video and output it as IMAGE (B,H,W,3 in [0,1]).
    - Use **video picker** (with upload button) or override with `video_path`.
    - Modes: first / last / index / time. Optional PNG save.
    """

    @classmethod
    def INPUT_TYPES(cls):
        # Build a video file list for the picker + upload
        input_dir = folder_paths.get_input_directory()
        try:
            files = [f for f in os.listdir(input_dir) if os.path.isfile(os.path.join(input_dir, f))]
        except FileNotFoundError:
            files = []
        files = folder_paths.filter_files_content_types(files, ["video"])
        files.sort()

        return {
            "required": {
                # keep 'video' REQUIRED so ComfyUI shows the upload button/preview
                "video": (files, {"video_upload": True}),
                "mode": (["first", "last", "index", "time"], {"default": "last"}),
            },
            "optional": {
                # optional manual override path (absolute/relative)
                "video_path": ("STRING", {"default": ""}),
                "frame_index": ("INT", {"default": 0, "min": 0}),
                "time_sec": ("FLOAT", {"default": 0.0, "min": 0.0}),
                "max_side": ("INT", {"default": 0, "min": 0, "max": 8192, "step": 4}),
                "save_png": ("BOOLEAN", {"default": False}),
                "save_path": ("STRING", {"default": ""}),
                "overwrite": ("BOOLEAN", {"default": True}),
            }
        }

    RETURN_TYPES = ("IMAGE", "STRING", "INT")
    RETURN_NAMES = ("image", "saved_path", "picked_index")
    FUNCTION = "run"
    CATEGORY = "SuiteTea/IO"

    def _resolve_video_path(self, annotated_name: str, override_path: str) -> str:
        if isinstance(override_path, str) and override_path.strip():
            p = os.path.abspath(override_path.strip())
        else:
            p = folder_paths.get_annotated_filepath(annotated_name)
        if not os.path.isfile(p):
            raise FileNotFoundError(f"LoadFrameFromVidAsImg: video not found → {p}")
        return p

    def _extract_frame_bytes(self, video_path: str, mode: str, frame_index: int, time_sec: float) -> Optional[bytes]:
        png = _extract_with_ffmpeg(video_path, mode, frame_index, time_sec)
        if png is None:
            png = _extract_with_opencv(video_path, mode, frame_index, time_sec)
        return png

    def run(
        self,
        video,                 # picker (annotated name)
        mode: str = "last",
        video_path: str = "",
        frame_index: int = 0,
        time_sec: float = 0.0,
        max_side: int = 0,
        save_png: bool = False,
        save_path: str = "",
        overwrite: bool = True,
    ):
        # Resolve real file path
        real_path = self._resolve_video_path(video, video_path)

        mode = str(mode).lower().strip()
        if mode not in {"first", "last", "index", "time"}:
            raise ValueError("mode must be one of: first, last, index, time")

        report_index = -1
        if mode == "index":
            frame_index = max(0, int(frame_index))
            report_index = frame_index
        time_sec = float(time_sec)

        png_bytes = self._extract_frame_bytes(real_path, mode, frame_index, time_sec)
        if png_bytes is None:
            raise RuntimeError("Failed to extract frame. Ensure ffmpeg is on PATH or install opencv-python.")

        img_t = _png_bytes_to_image_tensor(png_bytes)
        img_t = _resize_if_needed(img_t, max_side)

        saved = ""
        if save_png:
            out_path = save_path.strip() or _auto_save_name(real_path, mode, frame_index, time_sec)
            out_path = os.path.abspath(out_path)
            if (not overwrite) and os.path.exists(out_path):
                saved = out_path
            else:
                saved = _save_tensor_to_png(img_t, out_path)

        return (img_t, saved, report_index)
