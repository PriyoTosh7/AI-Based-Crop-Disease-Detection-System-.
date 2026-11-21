# Teacher Demonstration Guide

**Project:** AI-Based Crop Disease Detection and Smart Farming Assistance System  
**Model:** Fine-tuned EfficientNet-B3 · 39 PlantVillage classes · 300 × 300 input  
**Interface:** Bilingual English / Bangla  
**Architecture:** Frontend + FastAPI Backend + REST API + PostgreSQL + Grad-CAM

> Replace `YOUR-SERVICE` with the public URL after deployment. This guide intentionally uses public HTTPS links; do not present localhost links to the teacher.

## 1. Public links to open before the presentation

- **Live web application:** `https://YOUR-SERVICE.onrender.com/`
- **API health:** `https://YOUR-SERVICE.onrender.com/health`
- **Interactive API documentation:** `https://YOUR-SERVICE.onrender.com/docs`
- **OpenAPI JSON:** `https://YOUR-SERVICE.onrender.com/openapi.json`
- **Model information:** `https://YOUR-SERVICE.onrender.com/api/v1/model-info`
- **Research metrics:** `https://YOUR-SERVICE.onrender.com/api/v1/research-metrics`
- **PostgreSQL status:** `https://YOUR-SERVICE.onrender.com/api/v1/database-health`

Do not claim the app is live until `/health` returns HTTP 200, `model_loaded: true`, and the database endpoint reports `connected: true` if you intend to demonstrate history.

## 2. Five-to-seven-minute presentation flow

### Step 1 — Introduce the project (30 seconds)

Say: “This is a web-based crop disease decision-support system. The user uploads a crop leaf image, the frontend sends it to a FastAPI REST API, and a fine-tuned EfficientNet-B3 model returns its top predictions. PostgreSQL stores prediction metadata, and Grad-CAM provides a visual explanation of model attention.”

Show the dashboard and the system architecture section.

### Step 2 — Explain the model (45 seconds)

Open `/api/v1/model-info`. Show:
- EfficientNet-B3 architecture
- 39 trained classes
- 300 × 300 input
- Model inference device
- Checkpoint metadata and class order

Explain that the class order is loaded from the checkpoint, not manually guessed by the API.

### Step 3 — Live prediction (60–90 seconds)

Open the public application → **AI crop diagnosis** → choose a clear leaf photo → select **Single leaf (recommended)** → Analyze.

Explain the predicted class, top-1 score, confidence margin, top-5 probabilities and review status. Use a leaf photo from the same general style as the PlantVillage training data for the first demonstration.

### Step 4 — Background rejection (45 seconds)

Upload a non-leaf/background image. If the model selects `Background_without_leaves`, the application labels the result as background rejected and does not issue a disease diagnosis.

Explain: this is a trained background class, not a universal detector for every possible out-of-distribution image.

### Step 5 — Multiple-leaf / whole-plant mode (45 seconds)

Choose **Whole plant / multiple leaves (experimental)** and upload a wider plant image. The backend evaluates overlapping image crops and shows an aggregated prediction.

Important: describe this accurately as experimental multi-region classification. It is not an object detector, does not draw leaf bounding boxes, and has not been validated on a dedicated whole-plant field-image test set. Single-leaf mode remains recommended for the current trained model.

### Step 6 — Grad-CAM explainability (45 seconds)

Show the input crop, heatmap and overlay after prediction. Explain that Grad-CAM visualizes image regions that influenced the selected class score; it does not prove biological causation or confirm a diagnosis.

### Step 7 — PostgreSQL history (45 seconds)

Open **AI prediction history**. Show saved filename, predicted class, confidence, device and timestamp, plus class distribution. Confirm `/api/v1/database-health` before the presentation.

### Step 8 — API and research evidence (60 seconds)

Open `/docs`. Demonstrate `POST /api/v1/predict` or show its request schema. Then open `/api/v1/research-metrics` and show the recorded test-split metrics.

## 3. Research results and careful wording

The supplied root `outputs/confusion_matrix.npy`, `outputs/classwise_evaluation.csv` and `outputs/final_research_metrics.csv` agree on:

- Test images: 9,243
- Classes: 39
- Test accuracy: 98.8640%
- Macro precision: 98.6187%
- Macro recall: 98.6572%
- Macro F1: 98.6264%
- Potato Early Blight recall: 97.33% (150 test images)
- Potato Late Blight recall: 99.33% (150 test images)
- Background class: 172/172 correct in this confusion matrix

An older file under `outputs/evaluation/` reported 98.8532%. The evaluation artifacts have been regenerated from the supplied root confusion matrix to resolve this small stale-report discrepancy. State that these are PlantVillage test-split results, not guaranteed real-world field accuracy.

## 4. Known limitations to disclose

- The original raw 61,486-image dataset folder was not present in the uploaded ZIP. Its counts were supplied separately by the project owner; the ZIP did include the trained checkpoint and existing evaluation artifacts.
- The original dataset is class-folder PlantVillage-style data. Field images may differ in lighting, background, camera, variety and disease stage.
- Multi-region mode is exploratory crop tiling, not a trained object detector or validated whole-plant model.
- External field validation and additional labeled whole-plant data are required before making deployment-grade diagnostic claims.
- AI output is decision-support information, not a confirmed diagnosis or treatment prescription.

## 5. Teacher Q&A quick answers

**Q: Why EfficientNet-B3?**  
A: It is the architecture used by the supplied trained checkpoint and its 39-class output head.

**Q: How does the frontend communicate with the model?**  
A: The browser sends multipart image data to the FastAPI REST endpoint `POST /api/v1/predict`; FastAPI preprocesses the image and calls the PyTorch model.

**Q: Why PostgreSQL?**  
A: It stores prediction metadata so the application can display searchable history and aggregate analytics.

**Q: What does Grad-CAM do?**  
A: It visualizes regions that contributed to a selected model score. It is an interpretability aid, not proof of a disease.

**Q: Is 98.86% guaranteed in the field?**  
A: No. It is the recorded PlantVillage test-split accuracy. Independent field testing is still needed.

## 6. Final pre-demo checklist

- [ ] Public HTTPS application URL opens.
- [ ] `/health` returns HTTP 200 and `model_loaded: true`.
- [ ] `/api/v1/database-health` returns `connected: true` if showing history.
- [ ] A clear single-leaf photo returns a result.
- [ ] A background/non-leaf example is handled without a disease diagnosis if the model predicts the background class.
- [ ] Grad-CAM images load.
- [ ] Prediction history displays the new record.
- [ ] `/docs` opens and shows the REST API.
- [ ] No secrets, database passwords or private tokens are shown during the presentation.
