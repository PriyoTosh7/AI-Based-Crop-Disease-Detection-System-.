"""Load the supplied EfficientNet-B3 checkpoint, optionally downloading it for cloud deploys."""
from functools import lru_cache
import hashlib
import os
from pathlib import Path
import shutil
import urllib.request

import torch
import torch.nn as nn
from torchvision import models, transforms

PROJECT_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_CHECKPOINT = PROJECT_ROOT / "checkpoints" / "best_finetuned_efficientnet_b3.pth"
_raw_checkpoint_path = Path(os.getenv("PV_CHECKPOINT_PATH", str(DEFAULT_CHECKPOINT))).expanduser()
CHECKPOINT_PATH = _raw_checkpoint_path if _raw_checkpoint_path.is_absolute() else (PROJECT_ROOT / _raw_checkpoint_path).resolve()
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
IMAGE_SIZE = 300
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _ensure_checkpoint() -> None:
    expected_sha = os.getenv("PV_CHECKPOINT_SHA256", "").strip().lower()
    if CHECKPOINT_PATH.is_file():
        if expected_sha and _sha256(CHECKPOINT_PATH) != expected_sha:
            raise ValueError(f"Checkpoint SHA-256 mismatch: {CHECKPOINT_PATH}")
        return

    url = os.getenv("PV_CHECKPOINT_URL", "").strip()
    if not url:
        raise FileNotFoundError(
            f"Trained checkpoint not found: {CHECKPOINT_PATH}. Put the supplied file there "
            "or set PV_CHECKPOINT_URL to a downloadable model artifact URL."
        )

    CHECKPOINT_PATH.parent.mkdir(parents=True, exist_ok=True)
    temporary_path = CHECKPOINT_PATH.with_suffix(CHECKPOINT_PATH.suffix + ".part")
    request = urllib.request.Request(url, headers={"User-Agent": "CropCare-AI/1.0"})
    try:
        print(f"Downloading EfficientNet-B3 checkpoint from configured artifact URL: {url}")
        with urllib.request.urlopen(request, timeout=90) as response, temporary_path.open("wb") as output:
            shutil.copyfileobj(response, output, length=1024 * 1024)
        if temporary_path.stat().st_size < 1024 * 1024:
            raise ValueError("Downloaded checkpoint is unexpectedly small; check PV_CHECKPOINT_URL.")
        if expected_sha and _sha256(temporary_path) != expected_sha:
            raise ValueError("Downloaded checkpoint SHA-256 does not match PV_CHECKPOINT_SHA256.")
        temporary_path.replace(CHECKPOINT_PATH)
        print(f"Checkpoint downloaded: {CHECKPOINT_PATH} ({CHECKPOINT_PATH.stat().st_size:,} bytes)")
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise


@lru_cache(maxsize=1)
def load_model():
    _ensure_checkpoint()
    threads = max(1, int(os.getenv("TORCH_NUM_THREADS", "2")))
    torch.set_num_threads(threads)

    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=True)
    required = {"model_state_dict", "class_names"}
    missing = required.difference(checkpoint.keys())
    if missing:
        raise ValueError(f"Checkpoint is missing required keys: {sorted(missing)}")

    class_names = list(checkpoint["class_names"])
    num_classes = len(class_names)
    if num_classes != 39 or len(set(class_names)) != num_classes:
        raise ValueError(f"Expected 39 unique trained classes, found {num_classes}.")

    stored_num_classes = checkpoint.get("num_classes")
    if stored_num_classes is not None and int(stored_num_classes) != num_classes:
        raise ValueError("Checkpoint num_classes does not match its class_names list.")

    image_size = int(checkpoint.get("image_size", IMAGE_SIZE))
    if image_size != IMAGE_SIZE:
        raise ValueError(f"Expected training image size {IMAGE_SIZE}, checkpoint reports {image_size}.")

    # Cross-check the human-readable class metadata when it is present.
    class_file = PROJECT_ROOT / "outputs" / "model_export" / "class_names.json"
    if class_file.is_file():
        import json
        metadata_classes = json.loads(class_file.read_text(encoding="utf-8"))
        if metadata_classes != class_names:
            raise ValueError("Checkpoint class order differs from outputs/model_export/class_names.json.")

    model = models.efficientnet_b3(weights=None)
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(checkpoint["model_state_dict"], strict=True)
    model.to(DEVICE)
    model.eval()

    inference_transform = transforms.Compose([
        transforms.Resize(320),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    display_transform = transforms.Compose([
        transforms.Resize(320),
        transforms.CenterCrop(image_size),
    ])

    print("=" * 58)
    print("AI-BASED CROP DISEASE DETECTION SYSTEM")
    print("Model: EfficientNet-B3 | Classes:", num_classes)
    print("Image size:", image_size, "| Device:", DEVICE)
    print("Checkpoint:", CHECKPOINT_PATH.name)
    print("=" * 58)

    return {
        "model": model,
        "class_names": class_names,
        "num_classes": num_classes,
        "image_size": image_size,
        "transform": inference_transform,
        "display_transform": display_transform,
        "device": DEVICE,
        "architecture": "EfficientNet-B3",
        "checkpoint": CHECKPOINT_PATH.name,
        "checkpoint_path": str(CHECKPOINT_PATH),
        "checkpoint_epoch": checkpoint.get("epoch"),
        "checkpoint_val_accuracy": checkpoint.get("val_accuracy"),
    }
