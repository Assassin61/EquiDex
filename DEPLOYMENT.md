# FairProbe Cloud Setup Guide

This guide covers everything you need to know about setting up a live, decoupled deployment of FairProbe on Google Cloud Platform (Backend & Firebase) and Vercel (Frontend).

## Prerequisites
Before you start, you'll need the following:
1. A **Google Cloud Platform (GCP)** Account.
2. A **Vercel** Account.
3. A connected GitHub Repository natively hosting the FairProbe source code (we've pushed the code to the `demo-site` branch!).

---

## Part 1: Setting up the Firebase Database
Because FairProbe audits complex structures seamlessly over Google Cloud, we map the database structure directly to Firebase Firestore.

1. Navigate to your [Google Cloud Console](https://console.cloud.google.com).
2. Look for **Firebase / Firestore** in the project navigation elements. 
3. Initialize a **Firestore Database** choosing **Native Mode**.
4. Retrieve your Google Cloud **Project ID** from the upper-left dropdown on the console menu.
5. In your local FairProbe source code, open the file `fairprobe.config.yaml` and swap out the placeholder property string `"YOUR_PROJECT_ID"` inside the `database` section with your actual Project ID token.
6. Commit the final replacement string to sync your repository.

---

## Part 2: Deploying the Backend on Google Cloud Run
The backend is a dynamic API structure running entirely decoupled from frontend storage capabilities.

Since your terminal handles the logic configuration, you can use the `gcloud CLI` directly. 

1. Install Google Cloud SDK (`gcloud`) if you haven't yet, and authenticate using:
   ```bash
   gcloud auth login
   ```
2. Navigate directly into the local `/fairprobe` codebase via your internal system terminal.
3. Establish your deployment command indicating the unauthenticated, publicly visible application mapping:
   ```bash
   gcloud run deploy fairprobe-backend --source . --region us-central1 --allow-unauthenticated
   ```
4. Once the process completes, GCP will supply you with a newly generated URL referencing your backend route (E.g. *https://fairprobe-backend-XXXXX-uc.a.run.app*).
5. Open your codebase one final time and insert that custom route URL explicitly into the `window.FAIRPROBE_API_BASE` string assignment inside `frontend/js/config.js`!
6. Commit the frontend parameter mapping back up to the `demo-site` branch using git.

---

## Part 3: Deploying the Frontend on Vercel
Vercel handles all local environment UI parsing and HTML generation statically from the repo out-of-the-box via the `vercel.json` structure we've generated natively.

1. Open up the [Vercel Deployment Dashboard](https://vercel.com/new).
2. Select **"Import Git Repository"** and select the FairProbe repository you pushed earlier today.
3. Under the **"Branch to Deploy"** tab, verify and confirm the selection of branch `demo-site`.
4. Leave Vercel settings implicitly untouched! The platform will scan and interpret your mapped `vercel.json` pointing automatically at your `/frontend` folder endpoints.
5. Click **Deploy**.

It's that simple! Once Vercel indicates a green marker completion state, the link to your custom frontend URL acts as the centralized point for your deployed web platform.
