# Model artifact handling

## Why the checkpoint is not committed

`checkpoints/best_finetuned_efficientnet_b3.pth` is 112,224,178 bytes (about 107 MiB), above GitHub's 100 MB per-file limit. It is preserved in the delivered project ZIP but ignored by Git.

## Verify the supplied checkpoint

SHA-256:

`93625042ede1533f3a3cb563fe1432f3c3460532cf9cbbffe3bf9c269633dc4e`

Windows PowerShell:

```powershell
Get-FileHash .\checkpoints\best_finetuned_efficientnet_b3.pth -Algorithm SHA256
```

## Host it for public deployment

1. Create a public model repository on Hugging Face Hub (or use another HTTPS artifact host).
2. Upload the `.pth` file as `best_finetuned_efficientnet_b3.pth`.
3. Copy the direct file URL, typically `https://huggingface.co/ACCOUNT/REPOSITORY/resolve/main/best_finetuned_efficientnet_b3.pth`.
4. Set `PV_CHECKPOINT_URL` in the Render service environment.
5. Keep `PV_CHECKPOINT_SHA256` set to the checksum above.

The backend downloads the file to `PV_CHECKPOINT_PATH`, verifies its checksum and then loads it. The model is not automatically uploaded by this repository.
