# REST API examples

Replace `https://YOUR-SERVICE.onrender.com` with the deployed public HTTPS URL.

## Check health

```bash
curl https://YOUR-SERVICE.onrender.com/health
```

## Read model information

```bash
curl https://YOUR-SERVICE.onrender.com/api/v1/model-info
```

## Predict from a single leaf image

```bash
curl -X POST \
  -F "file=@potato-leaf.jpg" \
  -F "analysis_mode=single_leaf" \
  https://YOUR-SERVICE.onrender.com/api/v1/predict
```

## Experimental multi-region prediction

```bash
curl -X POST \
  -F "file=@whole-plant.jpg" \
  -F "analysis_mode=multi_region" \
  https://YOUR-SERVICE.onrender.com/api/v1/predict
```

The multi-region response includes `region_predictions` and `multi_region_limitation`. It is overlapping-crop classification, not object detection or validated whole-plant diagnosis.

## Generate Grad-CAM

```bash
curl -X POST \
  -F "file=@potato-leaf.jpg" \
  -F "target_class=Potato___Early_blight" \
  https://YOUR-SERVICE.onrender.com/api/v1/gradcam
```

## Read prediction history and analytics

```bash
curl "https://YOUR-SERVICE.onrender.com/api/v1/history?page=1&limit=10"
curl https://YOUR-SERVICE.onrender.com/api/v1/analytics
curl https://YOUR-SERVICE.onrender.com/api/v1/database-health
```

The history and analytics endpoints require a configured and reachable PostgreSQL database. The API schema is also available interactively at `/docs`.
