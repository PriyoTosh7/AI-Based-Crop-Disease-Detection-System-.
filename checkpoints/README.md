# Trained model artifact

The supplied EfficientNet-B3 checkpoint is intentionally not tracked by Git because it is approximately 112 MB and exceeds GitHub's 100 MB single-file limit.

Expected local path:

`checkpoints/best_finetuned_efficientnet_b3.pth`

SHA-256:

`93625042ede1533f3a3cb563fe1432f3c3460532cf9cbbffe3bf9c269633dc4e`

For cloud deployment, upload the checkpoint to a model-artifact host such as a public Hugging Face model repository and set `PV_CHECKPOINT_URL` to its direct `resolve/main` download URL. Set `PV_CHECKPOINT_SHA256` to the hash above. The backend downloads it atomically on first startup and verifies the checksum.
