# Teacher Presentation Script (Bangla)

**সময়:** প্রায় ৫–৭ মিনিট  
**Live URL:** `https://YOUR-SERVICE.onrender.com/`  
**API Docs:** `https://YOUR-SERVICE.onrender.com/docs`

## শুরুতে বলবে

“আমাদের Project-এর নাম AI-Based Crop Disease Detection and Smart Farming Assistance System। এটি একটি Web-Based Decision-Support System। এখানে Frontend, FastAPI Backend, REST API, PyTorch-এর EfficientNet-B3 Model এবং PostgreSQL Database একসঙ্গে কাজ করে।”

## Architecture বোঝাবে

“ব্যবহারকারী Frontend-এ ছবি Upload করেন। Frontend multipart request-এর মাধ্যমে FastAPI-এর `/api/v1/predict` Endpoint-এ ছবিটি পাঠায়। Backend Image Preprocessing করে EfficientNet-B3 Model-এ পাঠায়। Model ৩৯টি Class-এর মধ্যে Top Predictions দেয়। Prediction Metadata PostgreSQL-এ Save হয়। Grad-CAM Model-এর Attention বোঝাতে Heatmap তৈরি করে।”

## Live prediction দেখাবে

একটি পরিষ্কার পাতার ছবি Upload করে Single leaf mode নির্বাচন করবে। তারপর Top-1 Prediction, Confidence, Top-5 Result এবং Review Status দেখাবে।

## Background rejection বোঝাবে

“Background_without_leaves আমাদের Dataset-এর একটি আলাদা Class। Model এই Class-কে Top Prediction করলে আমরা রোগের নাম বা Treatment Suggestion দেখাই না।”

## Multiple leaf feature বোঝাবে

“Experimental Multi-region Mode-এ ছবির কয়েকটি Overlapping Crop আলাদাভাবে পরীক্ষা করা হয়। এটি Whole-plant Object Detection নয়; বর্তমান Model-এর জন্য একটি Experimental Feature।”

## Grad-CAM ও Database দেখাবে

“Grad-CAM Heatmap Model-এর Prediction-এ কোন Image Region ভূমিকা রেখেছে তা বোঝায়। PostgreSQL Prediction History সংরক্ষণ করে, ফলে আগের Prediction Search ও Analytics দেখা যায়।”

## Research metrics বোঝাবে

“আমাদের সরবরাহকৃত PlantVillage Test Split-এ ৯,২৪৩টি Test Image ও ৩৯টি Class-এর ওপর Recorded Accuracy 98.8640%। এটি Field Accuracy-এর নিশ্চয়তা নয়। বাস্তব কৃষিজমির ছবিতে আরও Independent Validation প্রয়োজন।”

## শেষ কথা

“এই Project-এর উদ্দেশ্য কৃষক ও কৃষি-সংশ্লিষ্ট ব্যক্তিদের প্রাথমিক সিদ্ধান্ত নিতে সহায়তা করা। এটি কৃষি বিশেষজ্ঞের নিশ্চিত রোগ নির্ণয়ের বিকল্প নয়।”
