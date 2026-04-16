# ── FairProbe Backend — Google Cloud Run ──────────────────────────────────────
FROM python:3.13-slim

# Non-root user for security
RUN addgroup --system appgroup && adduser --system --ingroup appgroup appuser

WORKDIR /app

# Install dependencies first (layer-cache friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY backend/ ./backend/
COPY fairprobe.config.yaml .
COPY demo_candidates.json .

# SQLite DB lives in /data which can be mounted as a volume or Cloud Run ephemeral FS
# For production use Firebase Firestore (change config type to "firebase")
ENV PORT=8080
ENV PYTHONUNBUFFERED=1
ENV PYTHONPATH=/app

# Run as non-root
USER appuser

EXPOSE 8080

CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8080"]
