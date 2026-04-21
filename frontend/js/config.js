/**
 * config.js — FairProbe Frontend Configuration
 *
 * In development: leave FAIRPROBE_API_BASE unset → defaults to localhost:8000
 * In production:  set this to your Cloud Run service URL BEFORE api.js loads,
 *                 OR just edit the line below directly.
 *
 * How to find your Cloud Run URL:
 *   gcloud run services describe fairprobe-backend \
 *     --region=us-central1 --format='value(status.url)'
 */

window.FAIRPROBE_API_BASE = 'https://fairprobe-backend-YOUR_PROJECT_ID.a.run.app'; // Replace with actual Cloud Run URL
