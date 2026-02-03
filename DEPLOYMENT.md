# 🚀 Deployment Guide

This guide explains how to deploy **Project Playto** using modern cloud platforms. We will separate the Backend (Railway) and Frontend (Vercel).

---

## 🏗️ 1. Deploying Backend (Railway)

We use **Railway** because it handles Django & PostgreSQL seamlessly.

### Steps:
1.  **Push to GitHub**:
    If you haven't initialized your repository yet, run these commands in your project folder:
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/Git-of-abhay/playto.git
    git push -u origin main
    ```
2.  **Sign Up/Login** to [Railway.app](https://railway.app/).
3.  **New Project** -> **Deploy from GitHub repo**.
4.  Select your repository.
5.  **Configure Service**:
    *   Railway usually detects Django automatically (via `requirements.txt` and `Procfile`).
6.  **Add Database**:
    *   Right click empty space -> **New** -> **Database** -> **PostgreSQL**.
    *   Railway acts magical here: it injects `DATABASE_URL` into your Django env automatically.
7.  **Environment Variables**:
    Go to your Django Service -> **Variables** tab. Add:
    *   `SECRET_KEY`: (Generate a random string)
    *   `DEBUG`: `False` (or just leave unset)
    *   `CORS_ALLOWED_ORIGINS`: `https://YOUR-VERCEL-FRONTEND-URL.vercel.app` (You will come back to update this after deploying frontend).
    *   `PORT`: `8000` (Optional, Railway usually detects).
8.  **Deploy**: Railway will build via `pip`, run standard build steps.
    *   *Note*: Interactions like Migrations often run automatically if configured in start command or manually via Railway CLI/Console.
    *   **Recommended Start Command** (in Settings ->/ Build&Deploy): `python manage.py migrate && gunicorn core.wsgi --log-file -`
9.  **Copy URL**: Get your public backend URL (e.g., `https://project-playto-production.up.railway.app`).

---

## 🎨 2. Deploying Frontend (Vercel)

We use **Vercel** for blazing fast React hosting.

### Steps:
1.  **Sign Up/Login** to [Vercel.com](https://vercel.com/).
2.  **Add New Project** -> Select your GitHub repo.
3.  **Configure Project**:
    *   **Framework Preset**: Vite (Automatic).
    *   **Root Directory**: `frontend` (Important! Click Edit and select the `frontend` folder).
4.  **Environment Variables**:
    *   `VITE_API_URL`: Paste your Railway Backend URL (e.g., `https://project-playto-production.up.railway.app`).
    *   **Note**: NO trailing slash is safer (`...app`, not `...app/`).
5.  **Deploy**: Click Deploy.
6.  **Finalize**:
    *   Copy your new Vercel domain (e.g., `https://project-playto.vercel.app`).
    *   **Go back to Railway Variables** and update `CORS_ALLOWED_ORIGINS` with this URL.
    *   **Redeploy Railway** (it usually restarts automatically on variable change).

---

## ✅ Verification
1.  Open your Vercel URL.
2.  Try to Log In / Sign Up.
3.  Upload an avatar (Resources served via Whitenoise/Railway functionality).
    *   *Note*: On Railway, uploaded files (media) are ephemeral (lost on restart) unless you attach a Volume or use AWS S3. For a demo, ephemeral is fine. For real interaction, consider configuring `django-storages` with S3.
