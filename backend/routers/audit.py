from fastapi import APIRouter, Request, UploadFile, File, HTTPException
from backend.demo_ai import run_batch
from backend.stats import calculate_all_stats, filter_by_period
import json
import os
import uuid
import csv
import io
from datetime import datetime

router = APIRouter(prefix="/audit", tags=["Audit"])


def load_candidates(config: dict) -> list:
    cache_path = config["demo"]["candidates_cache"]

    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    candidates = []

    # Name-to-ethnicity mapping for diverse candidate generation
    name_ethnicity_map = {
        "James Smith": "Caucasian",
        "John Davis": "Caucasian",
        "Michael Brown": "Caucasian",
        "Sarah Johnson": "Caucasian",
        "Emily White": "Caucasian",
        "Robert Wilson": "Caucasian",
        "Mohammed Hassan": "Middle Eastern",
        "Fatima Khan": "Middle Eastern",
        "Lakisha Williams": "African American",
        "Darius Jackson": "African American",
        "Aisha Patel": "South Asian",
        "Jamal Thompson": "African American",
        "Wei Zhang": "East Asian",
        "Priya Sharma": "South Asian",
        "Carlos Garcia": "Hispanic",
        "Maria Rodriguez": "Hispanic",
    }

    all_names = list(name_ethnicity_map.keys())
    target_count = config["demo"].get("candidates_count", 200)

    # Repeat names to reach target count
    repeats = max(1, target_count // len(all_names))

    for i, name in enumerate(all_names * repeats):
        if len(candidates) >= target_count:
            break
        candidates.append({
            "name": name,
            "age": 25 + (i % 30),
            "ethnicity": name_ethnicity_map[name],
            "experience": round(1 + (i % 8) + 0.5, 1),
            "gpa": round(2.5 + (i % 15) * 0.1, 1)
        })

    with open(cache_path, "w") as f:
        json.dump(candidates, f)

    return candidates


@router.post("/run")
async def run_audit(request: Request):
    config = request.app.state.config
    db = request.app.state.db

    audit_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    candidates = load_candidates(config)
    results = run_batch(candidates, config)

    for result in results:
        candidate = result["candidate"]
        db.save("applications", {
            "audit_id": audit_id,
            "name": candidate.get("name", ""),
            "age": candidate.get("age", 0),
            "ethnicity": candidate.get("ethnicity", "Unknown"),
            "experience": candidate.get("experience", 0),
            "gpa": candidate.get("gpa", 0),
            "decision": result["decision"],
            "score": result["score"],
            "timestamp": timestamp,
            "source": "demo"
        })

    db.save("audit_logs", {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "total_processed": len(results),
        "status": "completed"
    })

    return {
        "audit_id": audit_id,
        "total_processed": len(results),
        "status": "completed",
        "timestamp": timestamp
    }


ALLOWED_EXTENSIONS = {"csv", "json"}
REQUIRED_FIELDS = set()
VALID_DECISIONS = {"accepted", "rejected"}


def _parse_upload(content: bytes, filename: str) -> list:
    """
    Parses uploaded file bytes into a list of candidate dicts.
    Supports .csv and .json extensions.
    Raises HTTPException on bad format.
    """
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type '.{ext}'. Upload a .csv or .json file."
        )

    records = []

    if ext == "json":
        try:
            data = json.loads(content.decode("utf-8"))
        except (json.JSONDecodeError, UnicodeDecodeError) as e:
            raise HTTPException(status_code=422, detail=f"Invalid JSON: {e}")
        if not isinstance(data, list):
            raise HTTPException(status_code=422, detail="JSON must be a list of objects.")
        records = data

    elif ext == "csv":
        try:
            text = content.decode("utf-8")
            reader = csv.DictReader(io.StringIO(text))
            records = [dict(row) for row in reader]
        except UnicodeDecodeError:
            raise HTTPException(status_code=422, detail="CSV must be UTF-8 encoded.")

    if not records:
        raise HTTPException(status_code=422, detail="Uploaded file contains no records.")

    return records


@router.post("/upload")
async def upload_dataset(request: Request, file: UploadFile = File(...)):
    """
    Upload an existing dataset (CSV or JSON) for bias analysis.

    Optional fields (used in bias stats if present):
      - name, age, ethnicity, experience, gpa, score, decision
      
    If decision is omitted, it will be calculated using company_point_system config.
    """
    config = request.app.state.config
    db = request.app.state.db

    content = await file.read()
    records = _parse_upload(content, file.filename)

    audit_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()
    saved = 0
    skipped = 0

    for record in records:
        # Safely coerce optional numeric fields
        def safe_int(v, default=0):
            try:
                return int(float(v))
            except (TypeError, ValueError):
                return default

        def safe_float(v, default=0.0):
            try:
                return round(float(v), 2)
            except (TypeError, ValueError):
                return default

        decision = str(record.get("decision", "")).strip().lower()
        score = safe_float(record.get("score", 0))
        experience = safe_float(record.get("experience", 0))
        gpa = safe_float(record.get("gpa", 0))
        
        # If no decision provided, calculate natively via points system
        if not decision or decision not in VALID_DECISIONS:
            point_sys = config.get("company_point_system", {})
            multipliers = point_sys.get("multipliers", {})
            passing = point_sys.get("passing_score", 60)
            
            score = 0
            for key, mult in multipliers.items():
                val = safe_float(record.get(key, 0))
                score += val * mult
                
            decision = "accepted" if score >= passing else "rejected"

        db.save("applications", {
            "audit_id": audit_id,
            "name": str(record.get("name", "")).strip() or "Unknown",
            "age": safe_int(record.get("age", 0)),
            "ethnicity": str(record.get("ethnicity", "")).strip() or "Unknown",
            "experience": experience,
            "gpa": gpa,
            "decision": decision,
            "score": score,
            "timestamp": timestamp,
            "source": "uploaded"
        })
        saved += 1

    if saved == 0:
        raise HTTPException(
            status_code=422,
            detail=f"No valid records found in file."
        )

    db.save("audit_logs", {
        "audit_id": audit_id,
        "timestamp": timestamp,
        "total_processed": saved,
        "status": "completed"
    })

    return {
        "audit_id": audit_id,
        "total_processed": saved,
        "skipped": skipped,
        "source": "uploaded",
        "filename": file.filename,
        "status": "completed",
        "timestamp": timestamp,
        "next_steps": {
            "stats": f"/audit/{audit_id}/stats",
            "analyse": f"/action/analyse/{audit_id}",
            "report": f"/action/report/{audit_id}"
        }
    }


@router.get("/latest")
async def get_latest_audit(request: Request):
    db = request.app.state.db
    audit_id = db.get_latest_audit_id()

    if not audit_id:
        return {"audit_id": None, "message": "No audits run yet"}

    return {"audit_id": audit_id}


# /all/* routes MUST be before /{audit_id}/* routes
@router.get("/all/stats")
async def get_all_stats(request: Request):
    db = request.app.state.db
    config = request.app.state.config

    records = db.get_all("applications")
    stats = calculate_all_stats(records, config)

    return {
        "audit_id": "all",
        "period": "all_time",
        "total_audits": len(db.get_all("audit_logs")),
        "stats": stats
    }


@router.get("/all/applications")
async def get_all_applications(request: Request):
    db = request.app.state.db
    records = db.get_all("applications")

    return {
        "total": len(records),
        "applications": records
    }


@router.get("/{audit_id}/applications")
async def get_applications(audit_id: str, request: Request):
    db = request.app.state.db
    records = db.get_all("applications", audit_id)
    return {"audit_id": audit_id, "applications": records}


@router.get("/{audit_id}/stats")
async def get_stats(audit_id: str, request: Request, period: str = "all_time"):
    db = request.app.state.db
    config = request.app.state.config

    records = db.get_all("applications", audit_id)
    records = filter_by_period(records, period)
    stats = calculate_all_stats(records, config)

    return {
        "audit_id": audit_id,
        "period": period,
        "stats": stats
    }