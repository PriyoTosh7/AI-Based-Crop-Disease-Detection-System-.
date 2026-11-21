"""Single-leaf and experimental multi-region inference for the supplied 39-class model."""
import math

import torch
from PIL import Image

from backend.app.services.model_loader import load_model

try:
    from src.inference.disease_info import DISEASE_INFO
except Exception:
    DISEASE_INFO = {}

BACKGROUND_CLASS = "Background_without_leaves"
CONFIDENCE_THRESHOLD = 0.70
MARGIN_THRESHOLD = 0.15


def format_class_name(class_name: str) -> str:
    return class_name.replace("___", " - ").replace("_", " ").strip()


def get_disease_info(class_name: str):
    info = DISEASE_INFO.get(class_name)
    if info:
        return info
    if class_name == BACKGROUND_CLASS:
        return {
            "plant": "Unknown", "disease": "Background / no leaf detected",
            "type": "Background class", "pathogen": "Not applicable",
            "symptoms": ["The model classified the image as the trained background class.", "This is not a plant disease diagnosis."],
            "causes": ["No clear plant leaf may be present, or the image may resemble the background examples."],
            "prevention": ["Upload a clear, well-lit image focused on a plant leaf."],
            "management": ["Retake the photo with the leaf filling most of the frame."],
            "severity": "Not applicable",
            "note": "Background rejection is a trained class, not a universal out-of-distribution detector."
        }
    if class_name.endswith("___healthy"):
        plant = class_name.split("___", 1)[0].replace("_", " ")
        return {
            "plant": plant, "disease": "Healthy", "type": "Healthy Plant",
            "pathogen": "No pathogen class predicted",
            "symptoms": ["The model predicted the healthy class."],
            "causes": ["No disease class was the top prediction."],
            "prevention": ["Continue regular crop monitoring.", "Maintain balanced irrigation and nutrition.", "Use clean planting materials."],
            "management": ["Continue routine crop care and monitor for new symptoms."],
            "severity": "Healthy",
            "note": "A model prediction is not a field inspection. Confirm unusual symptoms with an agricultural expert."
        }
    return {
        "plant": class_name.split("___", 1)[0].replace("_", " "),
        "disease": format_class_name(class_name), "type": "Disease class",
        "pathogen": "Not specified in the supplied disease information database",
        "symptoms": ["Refer to local agricultural guidance and inspect the plant for matching symptoms."],
        "causes": ["The model matched this image to the corresponding PlantVillage class."],
        "prevention": ["Use healthy planting materials and maintain field hygiene."],
        "management": ["Confirm the diagnosis locally before choosing any treatment."],
        "severity": "Requires review",
        "note": "AI prediction is not a confirmed diagnosis. Verify symptoms before applying any treatment."
    }


def _multi_region_crops(image):
    """Return overlapping square crops. This is exploratory tiling, not leaf detection."""
    working = image.copy()
    working.thumbnail((1600, 1600), Image.Resampling.LANCZOS)
    width, height = working.size
    side = max(64, int(min(width, height) * 0.70))
    side = min(side, width, height)
    if side <= 0:
        return [(image, (0, 0, width, height))]
    xs = sorted({0, max(0, (width - side) // 2), max(0, width - side)})
    ys = sorted({0, max(0, (height - side) // 2), max(0, height - side)})
    regions = []
    for y in ys:
        for x in xs:
            box = (x, y, x + side, y + side)
            if box not in [item[1] for item in regions]:
                regions.append((working.crop(box), box))
    return regions[:9]


def predict_image(image, analysis_mode: str = "single_leaf"):
    if analysis_mode not in {"single_leaf", "multi_region"}:
        raise ValueError("analysis_mode must be 'single_leaf' or 'multi_region'.")

    bundle = load_model()
    model = bundle["model"]
    class_names = bundle["class_names"]
    rgb = image.convert("RGB")

    if analysis_mode == "multi_region":
        regions = _multi_region_crops(rgb)
        region_images = [item[0] for item in regions]
    else:
        regions = [(rgb, (0, 0, rgb.width, rgb.height))]
        region_images = [rgb]

    tensors = torch.stack([bundle["transform"](crop) for crop in region_images]).to(bundle["device"])
    with torch.inference_mode():
        logits = model(tensors)
        region_probabilities = torch.softmax(logits.float(), dim=1)
        probabilities = region_probabilities.mean(dim=0)

    top_k = min(5, len(class_names))
    top_probs, top_indices = torch.topk(probabilities, k=top_k)
    top_probs = top_probs.detach().cpu().tolist()
    top_indices = top_indices.detach().cpu().tolist()

    top_predictions = []
    for rank, (probability, class_index) in enumerate(zip(top_probs, top_indices), start=1):
        raw_name = class_names[int(class_index)]
        top_predictions.append({
            "rank": rank, "class_index": int(class_index), "class_name": raw_name,
            "label": format_class_name(raw_name), "probability": round(float(probability), 6),
            "confidence_percent": round(float(probability) * 100, 2),
        })

    predicted_class = top_predictions[0]["class_name"]
    confidence = float(top_probs[0])
    second_confidence = float(top_probs[1]) if len(top_probs) > 1 else 0.0
    margin = max(0.0, confidence - second_confidence)
    probabilities_list = probabilities.detach().cpu().tolist()
    entropy = -sum(float(p) * math.log(max(float(p), 1e-12)) for p in probabilities_list)
    normalized_entropy = entropy / math.log(len(class_names))

    background_index = class_names.index(BACKGROUND_CLASS) if BACKGROUND_CLASS in class_names else None
    background_probability = float(probabilities[background_index].detach().cpu().item()) if background_index is not None else 0.0
    is_background = predicted_class == BACKGROUND_CLASS
    is_healthy = predicted_class.endswith("___healthy")
    review_required = is_background or confidence < CONFIDENCE_THRESHOLD or margin < MARGIN_THRESHOLD

    if is_background:
        diagnosis_status = "background_rejected"
        reliability_status = "BACKGROUND CLASS — LEAF IMAGE NOT CONFIRMED"
    elif confidence < CONFIDENCE_THRESHOLD or margin < MARGIN_THRESHOLD:
        diagnosis_status = "review_required"
        reliability_status = "LOW / UNCERTAIN — REVIEW REQUIRED"
    elif is_healthy:
        diagnosis_status = "healthy"
        reliability_status = "HIGH MODEL CONFIDENCE"
    else:
        diagnosis_status = "disease_detected"
        reliability_status = "HIGH MODEL CONFIDENCE"

    region_predictions = []
    if analysis_mode == "multi_region":
        region_probs_cpu = region_probabilities.detach().cpu()
        for index, ((_, box), row) in enumerate(zip(regions, region_probs_cpu), start=1):
            score, class_index = torch.max(row, dim=0)
            raw_name = class_names[int(class_index)]
            region_predictions.append({
                "region": index,
                "box_xyxy": list(box),
                "class_name": raw_name,
                "label": format_class_name(raw_name),
                "confidence_percent": round(float(score) * 100, 2),
            })

    return {
        "predicted_class": predicted_class,
        "predicted_label": top_predictions[0]["label"],
        "confidence": round(confidence, 6),
        "confidence_percent": round(confidence * 100, 2),
        "second_confidence_percent": round(second_confidence * 100, 2),
        "confidence_margin": round(margin * 100, 2),
        "normalized_entropy": round(float(normalized_entropy), 6),
        "reliability_status": reliability_status,
        "diagnosis_status": diagnosis_status,
        "review_required": bool(review_required),
        "is_background": bool(is_background),
        "background_probability_percent": round(background_probability * 100, 2),
        "is_healthy": bool(is_healthy),
        "top_5_predictions": top_predictions,
        "analysis_mode": "multi_region_experimental" if analysis_mode == "multi_region" else "single_leaf",
        "region_count": len(regions),
        "region_predictions": region_predictions,
        "multi_region_limitation": (
            "Experimental overlapping-crop inference only. The classifier was trained on PlantVillage leaf-class images; "
            "this does not provide object detection or validated whole-plant disease diagnosis."
            if analysis_mode == "multi_region" else None
        ),
        "disease_info": get_disease_info(predicted_class),
        "architecture": bundle["architecture"],
        "device": str(bundle["device"]),
        "image_size": bundle["image_size"],
    }
