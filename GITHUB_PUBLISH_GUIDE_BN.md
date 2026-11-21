# GitHub-এ Project Publish করার বাংলা নির্দেশনা

## কোন ZIP ব্যবহার করবে?

- **GitHub Source ZIP**: GitHub-এ Push করার জন্য। এতে বড় `.pth` Model File ও Dataset নেই।
- **Full Project ZIP**: নিজের কাছে সম্পূর্ণ Project ও Trained Model Backup রাখার জন্য।

`.pth` Checkpoint-এর আকার 112,224,178 bytes—GitHub-এর 100 MB single-file limit-এর বেশি। তাই GitHub Source ZIP-এ এটি ইচ্ছাকৃতভাবে বাদ দেওয়া হয়েছে।

## ১. GitHub Repository তৈরি

1. GitHub-এ Sign in করো।
2. **New repository** নির্বাচন করো।
3. Repository name দাও: `AI-Based-Crop-Disease-Detection-System`
4. Public নির্বাচন করতে পারো, যদি Project Public দেখাতে চাও।
5. README বা .gitignore GitHub থেকে আগে তৈরি কোরো না; ZIP-এ এগুলো আছে।

## ২. Source ZIP Extract করো

একটি সহজ জায়গায় Extract করো। তারপর সেই Folder VS Code-এ Open করো।

## ৩. PowerShell-এ Commands চালাও

```powershell
git init
git add .
git status --short
```

`git status`-এ যেন `.env`, `*.pth`, `dataset/` বা `Plant_leave_diseases_dataset_with_augmentation/` না আসে। তারপর:

```powershell
git commit -m "Prepare CropCare AI teacher demo"
git branch -M main
git remote add origin https://github.com/YOUR-USERNAME/AI-Based-Crop-Disease-Detection-System.git
git push -u origin main
```

`YOUR-USERNAME`-এর জায়গায় নিজের GitHub username বসাবে।

## ৪. Model File আলাদাভাবে Host করো

1. Hugging Face-এ Account তৈরি করো।
2. একটি Public Model Repository তৈরি করো।
3. Full Project ZIP-এর `checkpoints/best_finetuned_efficientnet_b3.pth` ফাইল Upload করো।
4. ফাইলটির Direct `resolve/main` URL Copy করো।
5. Render-এর `PV_CHECKPOINT_URL` Environment Variable-এ URL বসাও।
6. SHA-256 এই মানের সঙ্গে মিলতে হবে:

```text
93625042ede1533f3a3cb563fe1432f3c3460532cf9cbbffe3bf9c269633dc4e
```

## ৫. Public Hosting

1. Hosted PostgreSQL Database তৈরি করো।
2. তার connection URL Copy করো।
3. Render-এ GitHub Repository Connect করো এবং Blueprint (`render.yaml`) Deploy করো।
4. `PV_CHECKPOINT_URL` ও `DATABASE_URL` Environment Variables দাও।
5. অন্তত 2 GB RAM-এর Instance নির্বাচন করো; PyTorch CPU inference-এর জন্য 4 GB বেশি নিরাপদ। Hosting-এর বর্তমান মূল্য দেখে নিও।
6. `/health`-এ HTTP 200 এবং `model_loaded: true` না পাওয়া পর্যন্ত Teacher Demo দেবে না।

## ৬. শিক্ষককে কী দেখাবে?

- Live Frontend: `https://YOUR-SERVICE.onrender.com/`
- Backend Health: `https://YOUR-SERVICE.onrender.com/health`
- API Documentation: `https://YOUR-SERVICE.onrender.com/docs`
- Model Info: `https://YOUR-SERVICE.onrender.com/api/v1/model-info`
- Research Metrics: `https://YOUR-SERVICE.onrender.com/api/v1/research-metrics`

শিক্ষককে দেখানোর সম্পূর্ণ ধাপ `TEACHER_DEMO_GUIDE.md` এবং `docs/Teacher_Demo_Presentation_Guide.docx`-এ আছে।
