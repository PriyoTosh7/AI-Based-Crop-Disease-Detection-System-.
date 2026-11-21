# Public deployment and GitHub guide

This project is configured as a **single-origin deployment**: FastAPI serves the HTML/CSS/JavaScript frontend and the `/api/v1/*` API from one public service. This avoids hard-coded localhost API URLs and avoids cross-origin configuration for the main deployment.

## Architecture

```text
Teacher / Student browser
          |
          | HTTPS public URL
          v
Render Docker Web Service
  |-- Frontend: HTML + CSS + JavaScript
  |-- Backend: FastAPI
  |-- API: /api/v1/* + /docs
  |-- Model: EfficientNet-B3 (CPU inference in cloud)
  |-- Grad-CAM image storage (ephemeral runtime storage)
          |
          v
Hosted PostgreSQL (DATABASE_URL)

Model artifact: public HTTPS download URL (PV_CHECKPOINT_URL)
```

## Before GitHub push

1. Confirm `.env` is not present in the repository root and never upload it.
2. Confirm the trained checkpoint exists locally at `checkpoints/best_finetuned_efficientnet_b3.pth`.
3. The checkpoint is ignored by Git because it is 112,224,178 bytes, above GitHub's 100 MB single-file limit. Upload it separately to a public model-artifact repository; see `docs/MODEL_ARTIFACT.md`.
4. The raw 61,486-image dataset is not included in the supplied ZIP and must not be committed to GitHub. The user-reported class counts can be audited locally by setting `PV_DATASET_DIR`.
5. From PowerShell in the project root:

```powershell
git init
git add .
git status --short
# Check that .env, dataset folders and *.pth files are NOT staged.
git commit -m "Prepare CropCare AI teacher demo"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/YOUR-REPOSITORY.git
git push -u origin main
```

If a `.pth` file appears in `git status`, stop and fix `.gitignore` before pushing. Do not force-push large model files.

## Deploy the public application on Render

1. Push the repository to GitHub.
2. Create a public model-artifact repository (e.g. Hugging Face) and upload the checkpoint. Copy its direct `resolve/main` URL.
3. Create a hosted PostgreSQL database with your chosen provider. Copy its connection URL. Use a provider's pooled URL if recommended.
4. In Render, choose **New → Blueprint** and select this GitHub repository. Render reads `render.yaml` and builds the Docker service.
5. In the Render service environment, set:
   - `PV_CHECKPOINT_URL` = direct HTTPS model download URL
   - `DATABASE_URL` = hosted PostgreSQL connection URL
   - `PV_CHECKPOINT_SHA256` = supplied checksum (already in Blueprint)
6. Choose a service instance with at least **2 GB RAM**; 4 GB is safer for PyTorch CPU inference. The configured `standard` plan may incur charges. Review current provider pricing before creating resources.
7. Wait for the first build and startup. The first startup downloads the ~107 MiB model artifact and loads EfficientNet-B3. The `/health` check must return HTTP 200 before presenting.
8. Copy the deployed public service URL, for example `https://YOUR-SERVICE.onrender.com`.

The same public origin provides:

- Frontend: `https://YOUR-SERVICE.onrender.com/`
- API health: `https://YOUR-SERVICE.onrender.com/health`
- API docs: `https://YOUR-SERVICE.onrender.com/docs`
- OpenAPI schema: `https://YOUR-SERVICE.onrender.com/openapi.json`
- Model info: `https://YOUR-SERVICE.onrender.com/api/v1/model-info`
- Research metrics: `https://YOUR-SERVICE.onrender.com/api/v1/research-metrics`
- PostgreSQL health: `https://YOUR-SERVICE.onrender.com/api/v1/database-health`

No localhost URL is needed for the teacher demonstration. The deployment is not performed automatically by this project; you must connect your GitHub, model artifact and database accounts and review any hosting charges.

## Database

The app creates the initial `prediction_history` table at startup when `DATABASE_URL` is valid. Prediction still works without PostgreSQL, but persistent history and analytics require the hosted database. Keep the database URL private.

## Operational notes

- The hosted service uses CPU inference unless deployed to a CUDA-enabled host.
- Grad-CAM images are stored in the service filesystem and may be removed when an ephemeral instance restarts. This does not affect prediction history.
- The checkpoint is downloaded at startup when it is absent. If the host has ephemeral storage, it may download again after a rebuild/restart.
- If hosting the frontend separately later, edit `frontend/config.js` to set `window.CROPCARE_API_BASE` to the public API origin and set `FRONTEND_ORIGINS` on the API service.
- Public demos should not collect personal or sensitive photos. The API does not persist the original uploaded photo; Grad-CAM renderings are temporarily written to server storage.
