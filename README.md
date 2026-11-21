# AI-Based Crop Disease Detection and Smart Farming Assistance System

A bilingual (English/Bangla) web application integrating a fine-tuned **EfficientNet-B3** classifier, **FastAPI REST API**, **PostgreSQL** prediction history and **Grad-CAM** visual explanations.

## What is included

- **Frontend:** HTML, CSS and JavaScript, served by FastAPI from the same public origin.
- **Backend:** FastAPI, image validation, preprocessing, inference, Grad-CAM and database integration.
- **REST API:** OpenAPI/Swagger documentation at `/docs`.
- **Model:** supplied EfficientNet-B3 checkpoint, 39 PlantVillage classes, 300 × 300 input.
- **Database:** SQLAlchemy + PostgreSQL for prediction metadata, history and analytics.
- **Research artifacts:** confusion matrix, class-wise reports, calibration metrics and figures.
- **Deployment:** Dockerfile and Render Blueprint for a public HTTPS deployment.
- **Teacher materials:** `TEACHER_DEMO_GUIDE.md` and `docs/TEACHER_PRESENTATION_SCRIPT.md`.

## Public deployment

The intended teacher demo is **not localhost**. Deploy the single Docker service using `render.yaml`; FastAPI serves the frontend and API together.

Read `DEPLOYMENT_GUIDE.md` for GitHub, model-artifact hosting, PostgreSQL and Render steps. You must supply your own hosting accounts and environment values. No deployment or GitHub push has been performed by this package.

Public routes after deployment:

| Purpose | Route |
|---|---|
| Frontend | `/` |
| Health | `/health` |
| Swagger API docs | `/docs` |
| OpenAPI schema | `/openapi.json` |
| Model info | `/api/v1/model-info` |
| Research metrics | `/api/v1/research-metrics` |
| Prediction | `POST /api/v1/predict` |
| Grad-CAM | `POST /api/v1/gradcam` |
| History | `/api/v1/history` |
| Analytics | `/api/v1/analytics` |
| Database health | `/api/v1/database-health` |

## Model artifact and GitHub file limit

The trained checkpoint is **112,224,178 bytes**, above GitHub's 100 MB per-file limit. It is preserved in the delivered ZIP but intentionally excluded from Git. Upload it separately to a public model artifact host and set `PV_CHECKPOINT_URL`. The backend verifies its SHA-256 before loading it. See `docs/MODEL_ARTIFACT.md`.

SHA-256: `93625042ede1533f3a3cb563fe1432f3c3460532cf9cbbffe3bf9c269633dc4e`

The raw 61,486-image dataset folder was not included in the supplied ZIP. It must remain outside GitHub. Its reported class counts were supplied by the project owner; the dataset itself was not available inside this archive for duplicate/near-duplicate scanning or retraining.

## Model inference behavior

- Single-leaf mode uses `Resize(320) → CenterCrop(300) → ToTensor → ImageNet normalization` to match the supplied validation transform.
- Experimental multi-region mode evaluates overlapping square crops and averages their class probabilities. It is **not** a leaf object detector and is not validated as whole-plant diagnosis. Use single-leaf mode for the current model.
- `Background_without_leaves` is a trained class. If it is the top prediction, the app rejects the image as a disease diagnosis.
- Top-1 confidence threshold (0.70) and margin threshold (0.15) are provisional review thresholds from the supplied notebook, not universal OOD guarantees.
- Grad-CAM shows image regions influencing the selected score; it is not biological proof.

## Recorded research results

The supplied root confusion matrix, class-wise evaluation and final metrics CSV agree on the following PlantVillage test-split results:

| Metric | Recorded value |
|---|---:|
| Test images | 9,243 |
| Classes | 39 |
| Accuracy | 98.8640% |
| Macro precision | 98.6187% |
| Macro recall | 98.6572% |
| Macro F1 | 98.6264% |
| ECE | 0.0028908 |
| Brier score | 0.0181845 |
| Negative log-likelihood | 0.0360748 |

The archived evaluation subfolder had a stale 98.8532% report. The evaluation JSON and confusion-pair artifacts have been regenerated from the supplied root confusion matrix (which matches `classwise_evaluation.csv` and `final_research_metrics.csv`). These are test-split results only; external field validation is required.

Potato class results from the same confusion matrix:

| Class | Test support | Recall |
|---|---:|---:|
| Potato Early Blight | 150 | 97.33% |
| Potato Late Blight | 150 | 99.33% |
| Potato Healthy | 150 | 99.33% |

## Dataset preparation (only if you have the raw dataset locally)

Place `Plant_leave_diseases_dataset_with_augmentation/` in the project root, or set `PV_DATASET_DIR` to its path. First run a dry audit:

```powershell
python -m src.data.inspect_dataset
python -m src.data.prepare_dataset --dry-run
```

Review the class counts and planned split. Then create `dataset/processed/{train,val,test}`:

```powershell
python -m src.data.prepare_dataset
```

The split script keeps byte-identical files in one split. It does not prove that visually similar augmented images are leakage-free; review augmentation provenance or run a dedicated perceptual-duplicate audit before making that claim. Existing splits are never overwritten.

The training loader checks the 39-class order against the checkpoint and uses `Resize(320) → CenterCrop(300)` for validation/test data. Windows defaults to `num_workers=0` for safe DataLoader startup. For evaluation/notebook dependencies, install `python -m pip install -r requirements-research.txt`.

## Environment variables

Copy `.env.example` to `.env` for local development or set the values in your cloud host dashboard. Never commit `.env`.

- `DATABASE_URL`: hosted PostgreSQL URL (required for persistent history).
- `PV_CHECKPOINT_URL`: direct HTTPS download URL for the checkpoint in cloud deploys.
- `PV_CHECKPOINT_PATH`: local/cloud checkpoint destination.
- `PV_CHECKPOINT_SHA256`: expected checkpoint checksum.
- `FRONTEND_ORIGINS`: optional comma-separated allowed origins if frontend is hosted separately.
- `MAX_UPLOAD_MB`: upload limit (default 10).
- `TORCH_NUM_THREADS`: CPU thread count (default 2).
- `GRADCAM_RETENTION_HOURS`: retention window for generated Grad-CAM files (default 24).

## Local development (optional; not the teacher demo target)

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
# Set DATABASE_URL if you want PostgreSQL history.
.\start_project.ps1
```

The local launcher is only for development/testing. The teacher presentation should use the public HTTPS URL after deployment.

## Validation

GitHub Actions performs Python compilation, frontend JavaScript syntax checks and required-file checks. For a local smoke test:

```powershell
python -m compileall -q backend src
node --check frontend/app.js
```

See `TEACHER_DEMO_GUIDE.md`, `docs/Teacher_Demo_Presentation_Guide.docx`, `docs/TEACHER_PRESENTATION_SCRIPT.md`, `DEPLOYMENT_GUIDE.md` and `GITHUB_PUBLISH_GUIDE_BN.md`.

## Responsible use

This application provides model estimates for research/educational decision support. It is not a confirmed diagnosis, does not prescribe treatment and should not replace an agricultural expert. Field validation is required before real-world operational use.
