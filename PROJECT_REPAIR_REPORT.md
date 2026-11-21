# Project Repair and Validation Report

## Summary

The uploaded ZIP was extracted and inspected. The existing EfficientNet-B3 checkpoint was preserved. The repository was updated for a single-origin public deployment where FastAPI serves the frontend and REST API together.

## Verified fixes

1. **Dataset source path:** the preparation and inspection scripts now discover the class-folder dataset at the project root or through `PV_DATASET_DIR`.
2. **Safe dataset split:** `prepare_dataset.py` has a dry-run mode, refuses to overwrite existing splits, and assigns byte-identical duplicate files to the same split. It explicitly does not claim that visually similar augmented copies have been fully deduplicated.
3. **DataLoader stability:** loader paths are configurable, class order is checked against the checkpoint, and Windows defaults to `num_workers=0` to avoid multiprocessing spawn issues.
4. **Evaluation checkpoint bug:** `evaluate_model.py` now defaults to the supplied `checkpoints/best_finetuned_efficientnet_b3.pth` and derives class count from `class_names`; the supplied checkpoint does not contain a `num_classes` key.
5. **Model validation:** the 39-class checkpoint loads successfully with EfficientNet-B3 and 300 × 300 preprocessing. Its class order matches `outputs/model_export/class_names.json`.
6. **Stale evaluation reports:** root confusion matrix and final class-wise metrics agree on 9,243 test images and 98.8640% accuracy. The old evaluation subfolder had 98.8532%; the JSON, classwise report, error analysis, confusion-pair files and confusion-matrix visuals were regenerated from the root confusion matrix.
7. **Frontend/API integration:** the frontend no longer hardcodes `127.0.0.1:8000`; it uses the same public origin by default, with an override in `frontend/config.js` if hosted separately.
8. **Single-origin hosting:** FastAPI now serves the frontend at `/`, API routes under `/api/v1/*`, Swagger at `/docs`, and OpenAPI at `/openapi.json`.
9. **Model artifact deployment:** the backend can download the checkpoint from `PV_CHECKPOINT_URL` and verify `PV_CHECKPOINT_SHA256`. The checkpoint is excluded from Git/Docker contexts because it exceeds GitHub's 100 MB file limit.
10. **Teacher materials:** added deployment instructions, system architecture, API examples, a Markdown demo guide, a Bangla presentation script and an editable DOCX teacher handout.
11. **Experimental multiple-leaf workflow:** added overlapping multi-region image crops, per-region predictions and a UI selection. This is explicitly marked experimental; it is not object detection and is not validated as whole-plant diagnosis.
12. **Grad-CAM storage:** generated Grad-CAM files are cleaned up after the configured retention window (default 24 hours).

## Validation performed in this environment

- Python source compilation: passed.
- JavaScript syntax checks (`app.js`, `data.js`, `config.js`): passed.
- EfficientNet-B3 checkpoint load: passed (CPU runtime in this environment; 39 classes, 300 input).
- Single-leaf prediction API smoke test: passed.
- Multi-region prediction API smoke test: passed (9 overlapping crops for the supplied sample image).
- Grad-CAM generation and retrieval of input/heatmap/overlay: passed.
- Frontend root, static assets, `/health`, `/docs`, `/openapi.json`, model-info and research-metrics routes: passed.
- Prediction history and analytics route flow: passed using an in-memory SQLite adapter to exercise the SQLAlchemy schema and route logic; actual PostgreSQL connectivity remains untested.
- Dataset split logic: passed on a small synthetic fixture, including exact duplicate grouping and dry-run behavior.
- Research metrics rebuilt from the supplied confusion matrix: 9,243 images, 9,138 correct, 105 incorrect, 98.8640% accuracy.

## Findings that could not be fully verified

1. **Raw dataset absent from the uploaded ZIP:** the project owner previously reported 61,486 images across 39 folders, but the raw `Plant_leave_diseases_dataset_with_augmentation` folder was not inside the ZIP. Therefore this repair pass could not scan the actual images, measure near-duplicate/augmentation leakage, create the real processed splits or retrain the model.
2. **Whole-plant model validation:** the existing checkpoint is a 39-class PlantVillage leaf classifier. Multi-region tiling is experimental; a true whole-plant/leaf detector requires additional labeled whole-plant images and a separate evaluation set.
3. **Real PostgreSQL:** the SQLAlchemy schema and history/analytics flow were smoke-tested with SQLite. No hosted PostgreSQL URL or credentials were supplied, so an actual PostgreSQL connection was not tested.
4. **Cloud artifact download:** the checksum and download mechanism are implemented, but no public model URL was supplied, so the remote download was not exercised.
5. **Public deployment/GitHub:** no repository credentials, model-hosting account or database credentials were supplied. Nothing was pushed or deployed. Follow `DEPLOYMENT_GUIDE.md` after adding the model artifact URL and hosted PostgreSQL URL.
6. **Docker cloud build:** the Dockerfile and Render Blueprint were prepared, but a remote Render build was not run.

## Recorded model evidence

From the supplied root confusion matrix and matching final classwise CSV:

- Overall test accuracy: 98.8640% (9,138 / 9,243)
- Macro precision: 98.6187%
- Macro recall: 98.6572%
- Macro F1: 98.6264%
- Potato Early Blight recall: 97.33% (150 test images)
- Potato Late Blight recall: 99.33% (150 test images)
- Background class: 172 / 172 correct in this confusion matrix

These are PlantVillage test-split metrics only, not field-accuracy guarantees.

## Required user actions before public teacher demo

1. Upload the checkpoint to a public model-artifact host and set `PV_CHECKPOINT_URL` in Render.
2. Create hosted PostgreSQL and set `DATABASE_URL` in Render.
3. Push the GitHub source package to the user's repository.
4. Deploy the Render Blueprint and wait for `/health` to return HTTP 200 with `model_loaded: true`.
5. Replace `YOUR-SERVICE` in the teacher guide with the actual public URL.
