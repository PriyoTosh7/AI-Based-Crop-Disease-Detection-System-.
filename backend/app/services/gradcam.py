"""
Grad-CAM for the supplied EfficientNet-B3.
The target layer model.features[-1] matches the uploaded training notebook.
"""
from datetime import datetime
import os
from pathlib import Path
from uuid import uuid4

import numpy as np
import torch
import torch.nn.functional as F
from PIL import Image

from backend.app.services.model_loader import load_model

PROJECT_ROOT = Path(__file__).resolve().parents[3]
GRADCAM_DIR = PROJECT_ROOT / "backend" / "storage" / "gradcam"
GRADCAM_DIR.mkdir(parents=True, exist_ok=True)
GRADCAM_RETENTION_HOURS = max(1, int(os.getenv("GRADCAM_RETENTION_HOURS", "24")))


def _cleanup_old_gradcam_files():
    cutoff = datetime.now().timestamp() - GRADCAM_RETENTION_HOURS * 3600
    for path in GRADCAM_DIR.glob("gradcam_*"):
        try:
            if path.is_file() and path.stat().st_mtime < cutoff:
                path.unlink(missing_ok=True)
        except OSError:
            pass


def _jet_colormap(gray: np.ndarray) -> Image.Image:
    x = np.clip(gray.astype(np.float32), 0.0, 1.0)
    red = np.clip(1.5 - np.abs(4.0 * x - 3.0), 0.0, 1.0)
    green = np.clip(1.5 - np.abs(4.0 * x - 2.0), 0.0, 1.0)
    blue = np.clip(1.5 - np.abs(4.0 * x - 1.0), 0.0, 1.0)
    rgb = np.stack([red, green, blue], axis=-1)
    return Image.fromarray(np.uint8(rgb * 255), mode="RGB")


def generate_gradcam(image: Image.Image, target_class: str | None = None):
    _cleanup_old_gradcam_files()
    bundle = load_model()
    model = bundle["model"]
    class_names = bundle["class_names"]
    device = bundle["device"]

    rgb = image.convert("RGB")
    input_tensor = bundle["transform"](rgb).unsqueeze(0).to(device)

    if target_class and target_class in class_names:
        target_index = class_names.index(target_class)
    else:
        target_index = None

    activations = {}
    gradients = {}
    target_layer = model.features[-1]

    def forward_hook(_module, _inputs, output):
        activations["value"] = output
        output.register_hook(lambda grad: gradients.__setitem__("value", grad))

    hook_handle = target_layer.register_forward_hook(forward_hook)

    try:
        model.eval()
        model.zero_grad(set_to_none=True)

        with torch.enable_grad():
            logits = model(input_tensor)
            probabilities = torch.softmax(logits.float(), dim=1)
            if target_index is None:
                target_index = int(torch.argmax(probabilities, dim=1).item())
            score = logits[0, target_index]
            score.backward()

        if "value" not in activations or "value" not in gradients:
            raise RuntimeError("Grad-CAM activations or gradients were not captured.")

        feature_maps = activations["value"].detach()
        grads = gradients["value"].detach()

        weights = grads.mean(dim=(2, 3), keepdim=True)
        cam = torch.relu((weights * feature_maps).sum(dim=1, keepdim=True))
        cam = F.interpolate(
            cam,
            size=(bundle["image_size"], bundle["image_size"]),
            mode="bilinear",
            align_corners=False,
        )[0, 0]

        cam = cam - cam.min()
        cam = cam / (cam.max() + 1e-8)
        cam_array = cam.detach().cpu().numpy()

        base_image = bundle["display_transform"](rgb).convert("RGB")
        heatmap = _jet_colormap(cam_array).resize(base_image.size, Image.Resampling.BILINEAR)
        overlay = Image.blend(base_image, heatmap, alpha=0.40)

        token = uuid4().hex
        base_name = f"gradcam_{token}"
        base_path = GRADCAM_DIR / f"{base_name}_input.png"
        heat_path = GRADCAM_DIR / f"{base_name}_heatmap.png"
        overlay_path = GRADCAM_DIR / f"{base_name}_overlay.png"

        base_image.save(base_path, format="PNG")
        heatmap.save(heat_path, format="PNG")
        overlay.save(overlay_path, format="PNG")

        confidence = float(probabilities[0, target_index].detach().cpu().item())
        return {
            "target_class": class_names[target_index],
            "target_label": class_names[target_index].replace("___", " - ").replace("_", " "),
            "confidence_percent": round(confidence * 100, 2),
            "target_layer": "model.features[-1]",
            "input_image_url": f"/storage/gradcam/{base_path.name}",
            "heatmap_url": f"/storage/gradcam/{heat_path.name}",
            "overlay_url": f"/storage/gradcam/{overlay_path.name}",
            "explanation": (
                "Grad-CAM highlights image regions that contributed to the selected model class. "
                "It is an explanation of model attention, not proof of disease."
            ),
        }
    finally:
        hook_handle.remove()
        model.zero_grad(set_to_none=True)
