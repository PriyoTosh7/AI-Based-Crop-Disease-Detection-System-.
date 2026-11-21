"""
FastAPI backend for:
AI-Based Crop Disease Detection and Smart Farming Assistance System

Model inference uses the supplied fine-tuned EfficientNet-B3 checkpoint.
"""
import csv
import logging
import os
from datetime import date, datetime, time, timedelta, timezone
from io import BytesIO
from pathlib import Path
from typing import Optional
from uuid import uuid4

from fastapi import FastAPI, File, Form, HTTPException, Query, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from PIL import Image, UnidentifiedImageError
from sqlalchemy import desc, func, or_

from backend.app.database.connection import Base, SessionLocal, engine
from backend.app.database.models import PredictionHistory
from backend.app.services.gradcam import generate_gradcam
from backend.app.services.model_loader import PROJECT_ROOT, load_model
from backend.app.services.predictor import predict_image

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("crop-disease-api")

PROJECT_TITLE = "AI-Based Crop Disease Detection and Smart Farming Assistance System"
FRONTEND_DIR = PROJECT_ROOT / "frontend"
OUTPUT_DIR = PROJECT_ROOT / "outputs"
STORAGE_DIR = PROJECT_ROOT / "backend" / "storage"
GRADCAM_DIR = STORAGE_DIR / "gradcam"
GRADCAM_DIR.mkdir(parents=True, exist_ok=True)

app = FastAPI(
    title=PROJECT_TITLE,
    description=(
        "Research demonstration application using a trained 39-class "
        "EfficientNet-B3 model, Grad-CAM explainability and PostgreSQL history."
    ),
    version="2.0.0",
)

_configured_origins = [item.strip() for item in os.getenv("FRONTEND_ORIGINS", "").split(",") if item.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_configured_origins or [
        "http://127.0.0.1:8000", "http://localhost:8000",
        "http://127.0.0.1:5501", "http://localhost:5501",
    ],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

app.mount("/storage", StaticFiles(directory=str(STORAGE_DIR)), name="storage")
if OUTPUT_DIR.is_dir():
    app.mount("/research-assets", StaticFiles(directory=str(OUTPUT_DIR)), name="research-assets")

DB_AVAILABLE = False
MODEL_AVAILABLE = False
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/webp", "image/bmp"}
MAX_UPLOAD_BYTES = max(1, int(os.getenv("MAX_UPLOAD_MB", "10"))) * 1024 * 1024


def _read_model_metadata():
    path = OUTPUT_DIR / "model_export" / "model_metadata.json"
    if path.is_file():
        try:
            import json
            return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            logger.exception("Could not read model metadata")
    return {}


def _read_research_metrics():
    path = OUTPUT_DIR / "final_research_metrics.csv"
    metrics = []
    if path.is_file():
        try:
            with path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    try:
                        metrics.append({
                            "metric": row.get("Metric", ""),
                            "value": float(row.get("Value", "nan")),
                        })
                    except (TypeError, ValueError):
                        continue
        except Exception:
            logger.exception("Could not read research metrics")
    return metrics


async def _decode_upload(file: UploadFile) -> Image.Image:
    if file.content_type and file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Only JPG, PNG, WebP and BMP images are supported.",
        )
    contents = await file.read()
    if not contents:
        raise HTTPException(status_code=400, detail="Uploaded image is empty.")
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(status_code=413, detail="Maximum image size is 10 MB.")
    try:
        probe = Image.open(BytesIO(contents))
        probe.verify()
        image = Image.open(BytesIO(contents)).convert("RGB")
        if image.width < 64 or image.height < 64:
            raise HTTPException(
                status_code=400,
                detail="Image must be at least 64 × 64 pixels.",
            )
        return image
    except HTTPException:
        raise
    except (UnidentifiedImageError, OSError, ValueError, Image.DecompressionBombError):
        raise HTTPException(status_code=400, detail="Invalid or corrupted image.")


def _refresh_database_status() -> bool:
    global DB_AVAILABLE
    if engine is None or SessionLocal is None:
        DB_AVAILABLE = False
        return False
    try:
        with engine.connect() as connection:
            connection.exec_driver_sql("SELECT 1")
        DB_AVAILABLE = True
    except Exception:
        DB_AVAILABLE = False
        logger.exception("PostgreSQL health probe failed")
    return DB_AVAILABLE


def _require_database():
    if not _refresh_database_status():
        raise HTTPException(
            status_code=503,
            detail="PostgreSQL is unavailable. Configure DATABASE_URL in the hosting environment.",
        )


@app.get("/")
def root():
    index_file = FRONTEND_DIR / "index.html"
    if not index_file.is_file():
        return {"project": PROJECT_TITLE, "status": "running", "api_docs": "/docs"}
    return FileResponse(index_file)


@app.get("/health")
def health_check():
    global MODEL_AVAILABLE
    try:
        bundle = load_model()
        MODEL_AVAILABLE = True
        return {
            "status": "healthy",
            "model_loaded": True,
            "architecture": bundle["architecture"],
            "classes": bundle["num_classes"],
            "image_size": bundle["image_size"],
            "device": str(bundle["device"]),
            "database_connected": DB_AVAILABLE,
        }
    except Exception as error:
        MODEL_AVAILABLE = False
        logger.exception("Model health check failed")
        raise HTTPException(status_code=503, detail=f"Model loading failed: {error}")


@app.get("/api/v1/status")
def system_status():
    return {
        "project": PROJECT_TITLE,
        "api": "online",
        "model": "loaded" if MODEL_AVAILABLE else "not_checked_or_unavailable",
        "database": "connected" if DB_AVAILABLE else "disconnected",
    }


@app.get("/api/v1/database-health")
def database_health():
    return {"database": "PostgreSQL", "connected": _refresh_database_status()}


@app.get("/api/v1/model-info")
def model_information():
    try:
        bundle = load_model()
        metadata = _read_model_metadata()
        return {
            "project": PROJECT_TITLE,
            "model": bundle["architecture"],
            "classes": bundle["num_classes"],
            "image_size": bundle["image_size"],
            "device": str(bundle["device"]),
            "checkpoint": bundle["checkpoint"],
            "checkpoint_epoch": bundle.get("checkpoint_epoch"),
            "checkpoint_validation_accuracy": bundle.get("checkpoint_val_accuracy"),
            "class_names": bundle["class_names"],
            "dataset": metadata.get("dataset", "PlantVillage"),
            "reported_test_accuracy": (
                round(float(metadata.get("test_accuracy")) * 100, 4)
                if metadata.get("test_accuracy") is not None and float(metadata.get("test_accuracy")) <= 1
                else metadata.get("test_accuracy")
            ),
            "reported_test_accuracy_unit": "percent",
            "reported_ece": metadata.get("ece"),
            "reported_brier_score": metadata.get("brier_score"),
        }
    except Exception as error:
        logger.exception("Model information unavailable")
        raise HTTPException(status_code=503, detail=str(error))


@app.get("/api/v1/research-metrics")
def research_metrics():
    metadata = _read_model_metadata()
    model_info = {}
    info_path = OUTPUT_DIR / "research_model_information.csv"
    if info_path.is_file():
        try:
            with info_path.open("r", encoding="utf-8-sig", newline="") as handle:
                for row in csv.DictReader(handle):
                    model_info[row.get("Parameter", "")] = row.get("Value", "")
        except Exception:
            logger.exception("Could not read research model information")
    return {
        "model": metadata.get("model_name", "EfficientNet-B3"),
        "dataset": metadata.get("dataset", "PlantVillage"),
        "classes": metadata.get("num_classes", 39),
        "training_images": int(float(model_info.get("Training Images", 43030))),
        "validation_images": int(float(model_info.get("Validation Images", 9213))),
        "testing_images": int(float(model_info.get("Testing Images", 9243))),
        "metrics": _read_research_metrics(),
        "note": (
            "Metrics are copied from the supplied final research evaluation files. "
            "They describe the recorded PlantVillage test split, not a guarantee "
            "of performance on arbitrary field photographs."
        ),
    }


@app.post("/api/v1/predict")
async def predict(
    file: UploadFile = File(...),
    analysis_mode: str = Form(default="single_leaf"),
):
    global DB_AVAILABLE
    try:
        if analysis_mode not in {"single_leaf", "multi_region"}:
            raise HTTPException(status_code=400, detail="analysis_mode must be 'single_leaf' or 'multi_region'.")
        image = await _decode_upload(file)
        result = predict_image(image, analysis_mode=analysis_mode)
        database_saved = False
        record_id = None

        if not DB_AVAILABLE:
            _refresh_database_status()
        if DB_AVAILABLE and SessionLocal is not None:
            db = SessionLocal()
            try:
                record = PredictionHistory(
                    filename=(Path(file.filename or "uploaded-image").name)[:255],
                    predicted_class=result["predicted_class"],
                    predicted_label=result["predicted_label"],
                    confidence=float(result["confidence"]),
                    confidence_percent=float(result["confidence_percent"]),
                    confidence_margin=float(result["confidence_margin"]),
                    top_5_predictions=result["top_5_predictions"],
                    architecture=result["architecture"],
                    device=result["device"],
                )
                db.add(record)
                db.commit()
                db.refresh(record)
                record_id = record.id
                database_saved = True
            except Exception:
                db.rollback()
                DB_AVAILABLE = False
                logger.exception("Could not save prediction to PostgreSQL")
            finally:
                db.close()

        return {
            "success": True,
            "filename": Path(file.filename or "uploaded-image").name,
            "database_saved": database_saved,
            "record_id": record_id,
            "result": result,
        }
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Prediction failed")
        raise HTTPException(status_code=500, detail=f"Prediction failed: {error}")
    finally:
        await file.close()


@app.post("/api/v1/gradcam")
async def gradcam(
    file: UploadFile = File(...),
    target_class: Optional[str] = Form(default=None),
):
    try:
        image = await _decode_upload(file)
        result = generate_gradcam(image, target_class=target_class)
        return {"success": True, **result}
    except HTTPException:
        raise
    except Exception as error:
        logger.exception("Grad-CAM generation failed")
        raise HTTPException(status_code=500, detail=f"Grad-CAM failed: {error}")
    finally:
        await file.close()


@app.get("/api/v1/history")
def get_prediction_history(
    page: int = Query(default=1, ge=1),
    limit: int = Query(default=10, ge=1, le=100),
    search: Optional[str] = None,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
):
    _require_database()
    db = SessionLocal()
    try:
        query = db.query(PredictionHistory)
        if search:
            pattern = f"%{search.strip()}%"
            query = query.filter(or_(
                PredictionHistory.filename.ilike(pattern),
                PredictionHistory.predicted_label.ilike(pattern),
                PredictionHistory.predicted_class.ilike(pattern),
            ))
        if start_date:
            start_dt = datetime.combine(start_date, time.min).replace(tzinfo=timezone.utc)
            query = query.filter(PredictionHistory.created_at >= start_dt)
        if end_date:
            end_dt = datetime.combine(end_date + timedelta(days=1), time.min).replace(tzinfo=timezone.utc)
            query = query.filter(PredictionHistory.created_at < end_dt)

        total = query.count()
        total_pages = max(1, (total + limit - 1) // limit)
        records = (
            query.order_by(desc(PredictionHistory.created_at), desc(PredictionHistory.id))
            .offset((page - 1) * limit)
            .limit(limit)
            .all()
        )
        return {
            "success": True,
            "total_records": total,
            "page": page,
            "limit": limit,
            "total_pages": total_pages,
            "history": [
                {
                    "id": item.id,
                    "filename": item.filename,
                    "predicted_class": item.predicted_class,
                    "predicted_label": item.predicted_label,
                    "confidence": item.confidence,
                    "confidence_percent": item.confidence_percent,
                    "confidence_margin": item.confidence_margin,
                    "top_5_predictions": item.top_5_predictions,
                    "architecture": item.architecture,
                    "device": item.device,
                    "created_at": item.created_at.isoformat(),
                }
                for item in records
            ],
        }
    finally:
        db.close()


@app.get("/api/v1/analytics")
def prediction_analytics():
    _require_database()
    db = SessionLocal()
    try:
        total = db.query(func.count(PredictionHistory.id)).scalar() or 0
        avg_confidence = db.query(func.avg(PredictionHistory.confidence_percent)).scalar()
        grouped = (
            db.query(PredictionHistory.predicted_class, func.count(PredictionHistory.id))
            .group_by(PredictionHistory.predicted_class)
            .order_by(desc(func.count(PredictionHistory.id)))
            .all()
        )
        distribution = [
            {
                "class_name": class_name,
                "label": class_name.replace("___", " - ").replace("_", " "),
                "count": int(count),
                "is_background": class_name == "Background_without_leaves",
            }
            for class_name, count in grouped
        ]
        background_count = sum(x["count"] for x in distribution if x["is_background"])
        disease_count = total - background_count
        return {
            "success": True,
            "total_predictions": int(total),
            "disease_predictions": int(disease_count),
            "background_rejections": int(background_count),
            "unique_classes": len([x for x in distribution if not x["is_background"]]),
            "average_confidence_percent": round(float(avg_confidence or 0.0), 2),
            "distribution": [x for x in distribution if not x["is_background"]][:10],
        }
    finally:
        db.close()


@app.on_event("startup")
async def startup_event():
    global DB_AVAILABLE, MODEL_AVAILABLE

    logger.info("Starting %s", PROJECT_TITLE)

    try:
        bundle = load_model()
        MODEL_AVAILABLE = True
        logger.info(
            "Trained model loaded: %s (%s classes) on %s",
            bundle["architecture"],
            bundle["num_classes"],
            bundle["device"],
        )
    except Exception:
        MODEL_AVAILABLE = False
        logger.exception("Trained model could not be loaded")

    if engine is not None and SessionLocal is not None:
        try:
            Base.metadata.create_all(bind=engine)
            with engine.connect() as connection:
                connection.exec_driver_sql("SELECT 1")
            DB_AVAILABLE = True
            logger.info("PostgreSQL connected; prediction_history table is ready.")
        except Exception:
            DB_AVAILABLE = False
            logger.exception("PostgreSQL unavailable; API will run without history persistence.")
    else:
        DB_AVAILABLE = False
        logger.warning("DATABASE_URL not configured. Prediction API will run without database saving.")


# Serve the production frontend from the same public origin as the API.
# Keep this mount last so /docs, /openapi.json and /api/* routes take precedence.
app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="frontend")
