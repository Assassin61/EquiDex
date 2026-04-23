# EquiDex Cloud Setup Guide

This guide covers deploying EquiDex with **Firebase Hosting** (frontend) + **Google Cloud Run** (backend) + **Firebase Firestore** (database).

## Prerequisites
1. A **Google Cloud Platform (GCP)** account with a project created.
2. **Firebase CLI** installed (`npm install -g firebase-tools`).
3. **gcloud CLI** installed and authenticated.
4. A connected GitHub repository with the EquiDex source code.

---

## Part 1: Setting up the Firebase Database (Firestore)

1. Navigate to your [Google Cloud Console](https://console.cloud.google.com).
2. Open **Firestore** and create a database in **Native Mode**.
3. Copy your GCP **Project ID** from the console.
4. In `fairprobe.config.yaml`, update the `database` section:
   ```yaml
   database:
     type: "firebase"
     project_id: "YOUR_PROJECT_ID"
   ```
5. In `.firebaserc`, replace `YOUR_PROJECT_ID` with your actual project ID.
6. Commit and push.

---

## Part 2: Deploying the Backend on Google Cloud Run

1. Authenticate with gcloud:
   ```bash
   gcloud auth login
   gcloud config set project YOUR_PROJECT_ID
   ```

2. Set your Gemini API key as a secret:
   ```bash
   gcloud run deploy equidex-backend \
     --source . \
     --region us-central1 \
     --allow-unauthenticated \
     --set-env-vars GEMINI_API_KEY=your_key_here
   ```

3. After deployment, copy the generated URL (e.g. `https://equidex-backend-XXXXX-uc.a.run.app`).

4. Update `frontend/js/config.js` with your backend URL:
   ```js
   window.EQUIDEX_API_BASE = 'https://equidex-backend-XXXXX-uc.a.run.app';
   ```

5. Also add your Firebase Hosting domain to the CORS origins in `backend/main.py`:
   ```python
   allow_origins=[
       "https://YOUR_PROJECT_ID.web.app",
       "https://YOUR_PROJECT_ID.firebaseapp.com",
   ]
   ```

---

## Part 3: Deploying the Frontend on Firebase Hosting

The `firebase.json` is already configured to serve from the `frontend/` directory.

1. Login to Firebase:
   ```bash
   firebase login
   ```

2. Deploy:
   ```bash
   firebase deploy --only hosting
   ```

3. Your frontend will be live at `https://YOUR_PROJECT_ID.web.app`.

---

## Alternative: Frontend on Vercel

If you prefer Vercel over Firebase Hosting, the `vercel.json` is also configured.

1. Go to [vercel.com/new](https://vercel.com/new) and import your repository.
2. Select the branch to deploy (e.g. `main` or `demo-site`).
3. Vercel will detect `vercel.json` and serve the `frontend/` directory automatically.
4. Click **Deploy**.

> **Note:** If using Vercel for the frontend, add your Vercel URL to the CORS origins in `backend/main.py`.

---

## TLS / HTTPS

Both Firebase Hosting and Vercel automatically provide TLS certificates (HTTPS) for your deployed sites. Google Cloud Run also serves over HTTPS by default. **No manual TLS configuration is needed for production.**

For local development, the app runs over plain HTTP on `http://127.0.0.1:8000` (backend) and `http://127.0.0.1:3000` (frontend). Self-signed certificates for local HTTPS can be generated using `python generate_cert.py` if needed.
