from fastapi import APIRouter, Request
from backend.demo_ai import evaluate_candidate, run_batch
from backend.stats import calculate_all_stats
import json
import os
import uuid
from datetime import datetime

router = APIRouter(prefix="/audit", tags=["Audit"])


def load_candidates(config: dict) -> list:
    """
    Loads candidates from cache file.
    If cache doesn't exist, generates basic demo candidates.
    """
    cache_path = config["demo"]["candidates_cache"]

    if os.path.exists(cache_path):
        with open(cache_path, "r") as f:
            return json.load(f)

    # Basic demo candidates if no cache exists
    candidates = []
    names_western = ["James Smith", "John Davis", "Michael Brown",
                     "Sarah Johnson", "Emily White", "Robert Wilson"]
    names_non_western = ["Mohammed Hassan", "Fatima Khan", "Lakisha Williams",
                         "Darius Jackson", "Aisha Patel", "Jamal Thompson"]

    all_names = names_western + names_non_western

    for i, name in enumerate(all_names * 10):
        candidates.append({
            "name": name,
            "age": 25 + (i % 30),
            "ethnicity": "Middle Eastern" if any(
                n in name for n in ["Mohammed", "Fatima", "Aisha"]
            ) else "Caucasian",
            "experience": round(1 + (i % 8) + 0.5, 1),
            "gpa": round(2.5 + (i % 15) * 0.1, 1)
        })

    # Save to cache
    with open(cache_path, "w") as f:
        json.dump(candidates, f)

    return candidates


@router.post("/run")
async def run_audit(request: Request):
    """
    Runs the full audit pipeline.
    Loads candidates → feeds to demo AI → logs to database.
    """
    config = request.app.state.config
    db = request.app.state.db

    # Generate unique audit ID
    audit_id = str(uuid.uuid4())[:8]
    timestamp = datetime.now().isoformat()

    # Load candidates
    candidates = load_candidates(config)

    # Run through demo hiring AI
    results = run_batch(candidates, config)

    # Save every decision to database
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

    # Log audit run
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


@router.get("/latest")
async def get_latest_audit(request: Request):
    """
    Returns the most recent audit ID.
    Frontend uses this to know which audit to display.
    """
    db = request.app.state.db
    audit_id = db.get_latest_audit_id()

    if not audit_id:
        return {"audit_id": None, "message": "No audits run yet"}

    return {"audit_id": audit_id}


@router.get("/{audit_id}/applications")
async def get_applications(audit_id: str, request: Request):
    """
    Returns all applications for a specific audit.
    """
    db = request.app.state.db
    records = db.get_all("applications", audit_id)
    return {"audit_id": audit_id, "applications": records}


@router.get("/{audit_id}/stats")
async def get_stats(
    audit_id: str,
    request: Request,
    period: str = "all_time"
):
    """
    Returns calculated bias statistics for a specific audit.
    FastAPI does all the math here — Gemini never touches numbers.
    """
    from backend.stats import filter_by_period

    db = request.app.state.db
    config = request.app.state.config

    # Fetch records
    records = db.get_all("applications", audit_id)

    # Filter by time period
    records = filter_by_period(records, period)

    # Calculate stats
    stats = calculate_all_stats(records, config)

    return {
        "audit_id": audit_id,
        "period": period,
        "stats": stats
    }