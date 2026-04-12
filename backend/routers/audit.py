from fastapi import APIRouter, Request
from backend.demo_ai import run_batch
from backend.stats import calculate_all_stats, filter_by_period
import json
import os
import uuid
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