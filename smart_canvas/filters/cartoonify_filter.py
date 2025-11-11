import os
import torch
import numpy as np
from PIL import Image
import cv2
from cv2.typing import MatLike
from smart_canvas.filters.base import Filter


# --------------------------- CONFIG ---------------------------
CONFIG = {
    "BACKEND": "animegan",  # "animegan" or "classical"
    "ANIME_PRESET": "face_paint_512_v2",
    "ANIME_SIZE": 768,
    "DEVICE": "auto",  # auto-select: CUDA > MPS > CPU
    "EDGE_STRENGTH": 1.0,
    "SMOOTH": 7,
    "BILATERAL_ITER": 4,
}
# --------------------------------------------------------------


def _get_device(device_str: str) -> torch.device:
    """Returns best available torch device based on input or availability."""
    if device_str == "auto":
        if torch.cuda.is_available():
            return torch.device("cuda")
        elif torch.backends.mps.is_available():
            return torch.device("mps")
        else:
            return torch.device("cpu")
    else:
        return torch.device(device_str)


def _nearest_multiple(x: int, m: int = 32) -> int:
    return max(m, int(round(x / m)) * m)


def resize_to_multiple(img: Image.Image, short_side: int = 512, mult: int = 32) -> Image.Image:
    w, h = img.size
    scale = short_side / min(w, h)
    new_w, new_h = int(round(w * scale)), int(round(h * scale))
    new_w, new_h = _nearest_multiple(new_w, mult), _nearest_multiple(new_h, mult)
    return img.resize((new_w, new_h), Image.BICUBIC)


def pil_to_tensor(img: Image.Image, device: torch.device) -> torch.Tensor:
    arr = np.asarray(img).astype(np.float32) / 255.0
    arr = arr.transpose(2, 0, 1)
    t = torch.from_numpy(arr).unsqueeze(0).to(device)
    return t * 2.0 - 1.0


def tensor_to_pil(t: torch.Tensor) -> Image.Image:
    t = (t.clamp_(-1, 1) + 1.0) / 2.0
    t = (t * 255.0).byte().cpu().squeeze(0).numpy().transpose(1, 2, 0)
    return Image.fromarray(t)


def _animegan_backend(img: Image.Image, cfg: dict) -> Image.Image:
    dev = _get_device(cfg["DEVICE"])
    model = torch.hub.load(
        "bryandlee/animegan2-pytorch:main",
        "generator",
        pretrained=cfg["ANIME_PRESET"],
    ).to(dev).eval()

    with torch.no_grad():
        img_resized = resize_to_multiple(img, short_side=cfg["ANIME_SIZE"], mult=32)
        t = pil_to_tensor(img_resized, dev)
        out = model(t)
    return tensor_to_pil(out)


def _classical_backend(img: Image.Image, cfg: dict) -> Image.Image:
    edge_strength = cfg["EDGE_STRENGTH"]
    smooth = cfg["SMOOTH"]
    bilateral_iter = cfg["BILATERAL_ITER"]

    bgr = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
    gray = cv2.medianBlur(gray, 7)
    edges = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_MEAN_C, cv2.THRESH_BINARY, 9, 9)

    color = bgr.copy()
    for _ in range(max(1, bilateral_iter)):
        color = cv2.bilateralFilter(color, d=smooth, sigmaColor=200, sigmaSpace=200)

    Z = color.reshape((-1, 3)).astype(np.float32)
    K = 16
    criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 20, 0.5)
    _, labels, centers = cv2.kmeans(Z, K, None, criteria, 1, cv2.KMEANS_PP_CENTERS)
    quant = centers[labels.flatten()].reshape(color.shape).astype(np.uint8)

    edges = cv2.cvtColor(edges, cv2.COLOR_GRAY2BGR)
    if edge_strength != 1.0:
        e = np.clip((edges.astype(np.float32) - 128) * edge_strength + 128, 0, 255).astype(np.uint8)
        edges = e
    cartoon = cv2.bitwise_and(quant, edges)
    out = cv2.cvtColor(cartoon, cv2.COLOR_BGR2RGB)
    return Image.fromarray(out)


def cartoonize_image(image_or_path, config: dict = CONFIG) -> Image.Image:
    """
    Takes an image path or PIL.Image, returns cartoonized PIL.Image.
    Works on CPU, CUDA, or MPS automatically.
    """
    try:
        if isinstance(image_or_path, str):
            if not os.path.isfile(image_or_path):
                raise FileNotFoundError(f"Input not found: {image_or_path}")
            img = Image.open(image_or_path).convert("RGB")
        elif isinstance(image_or_path, Image.Image):
            img = image_or_path.convert("RGB")
        else:
            raise TypeError("Input must be a file path or PIL.Image.Image")

        backend = config["BACKEND"].lower()
        if backend == "animegan":
            out_img = _animegan_backend(img, config)
        elif backend == "classical":
            out_img = _classical_backend(img, config)
        else:
            raise ValueError("BACKEND must be 'animegan' or 'classical'")

        return out_img

    except Exception as e:
        print(f"[ERROR] Cartoonization failed: {e}")
        raise


class CartoonifyFilter(Filter):
    """
    Cartoonify filter using AnimeGAN or classical cartoon effect.
    """
    background = 'cartoon_bg.png'
    
    def __init__(self):
        super().__init__()
        self.config = CONFIG.copy()
        # Use classical backend for the background to reduce processing time
        self.bg_config = CONFIG.copy()
        self.bg_config["BACKEND"] = "classical"  # Faster for background processing
        # self.bg_config["BACKEND"] = "animegan"  # More computationally intensive

    
    def filter(self, frame: MatLike) -> MatLike:
        """
        Apply cartoonify effect to the camera frame.
        """
        try:
            # Convert OpenCV BGR frame to RGB PIL Image
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            
            # cartoonization
            cartoon_pil = cartoonize_image(pil_img, self.config)
            
            # back to OpenCV BGR format
            cartoon_rgb = np.array(cartoon_pil)
            cartoon_bgr = cv2.cvtColor(cartoon_rgb, cv2.COLOR_RGB2BGR)
            
            # Resizing to match original frame size if needed
            if cartoon_bgr.shape[:2] != frame.shape[:2]:
                cartoon_bgr = cv2.resize(cartoon_bgr, (frame.shape[1], frame.shape[0]))
            
            return cartoon_bgr
            
        except Exception as e:
            print(f"[WARN] Cartoonify filter failed: {e}")
            # Return original frame on error
            return frame
    
    def background_filter(self, frame: MatLike) -> MatLike:
        """
        Apply cartoon effect to the background image for animated appearance.
        Uses classical backend for faster processing.
        """
        try:
            # background to PIL Image
            bg_rgb = cv2.cvtColor(self.bg_image, cv2.COLOR_BGR2RGB)
            bg_pil = Image.fromarray(bg_rgb)
            
            # Apply classical cartoon effect to background (faster than AnimeGAN)
            cartoon_bg_pil = cartoonize_image(bg_pil, self.bg_config)
            
            # Convert back to OpenCV BGR format
            cartoon_bg_rgb = np.array(cartoon_bg_pil)
            cartoon_bg_bgr = cv2.cvtColor(cartoon_bg_rgb, cv2.COLOR_RGB2BGR)
            
            return cartoon_bg_bgr
            
        except Exception as e:
            print(f"[WARN] Background cartoonify failed: {e}")
            # Return original background on error
            return self.bg_image
