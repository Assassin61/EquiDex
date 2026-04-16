from fastapi import APIRouter, Request, HTTPException
from backend.gemini import analyse_bias, generate_report, summarize_report
from backend.stats import calculate_all_stats
import json
import datetime

router = APIRouter(prefix="/action", tags=["Actions"])


@router.post("/analyse/{audit_id}")
async def analyse(audit_id: str, request: Request):
    db = request.app.state.db
    config = request.app.state.config

    records = db.get_all("applications", audit_id)
    if not records:
        raise HTTPException(status_code=404, detail="Audit not found")

    stats = calculate_all_stats(records, config)
    analysis = await analyse_bias(stats, config)

    # Save to reports table
    db.save("reports", {
        "audit_id": audit_id,
        "timestamp": datetime.datetime.now().isoformat(),
        "analysis": json.dumps(analysis),
        "formal_report": "",
        "summary": ""
    })

    return {"audit_id": audit_id, "analysis": analysis}


@router.post("/report/{audit_id}")
async def report(audit_id: str, request: Request):
    db = request.app.state.db
    config = request.app.state.config

    records = db.get_all("applications", audit_id)
    if not records:
        raise HTTPException(status_code=404, detail="Audit not found")

    stats = calculate_all_stats(records, config)
    analysis = await analyse_bias(stats, config)
    formal_report = await generate_report(analysis, stats, config)

    # Update reports table
    existing = db.get_all("reports", audit_id)
    if existing:
        db.update("reports", {"formal_report": formal_report}, audit_id)
    else:
        db.save("reports", {
            "audit_id": audit_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": json.dumps(analysis),
            "formal_report": formal_report,
            "summary": ""
        })

    return {"audit_id": audit_id, "report": formal_report}


@router.post("/summarize/{audit_id}")
async def summarize(audit_id: str, request: Request):
    db = request.app.state.db
    config = request.app.state.config

    records = db.get_all("applications", audit_id)
    if not records:
        raise HTTPException(status_code=404, detail="Audit not found")

    stats = calculate_all_stats(records, config)
    analysis = await analyse_bias(stats, config)
    formal_report = await generate_report(analysis, stats, config)
    summary = await summarize_report(formal_report, config)

    # Update reports table
    existing = db.get_all("reports", audit_id)
    if existing:
        db.update("reports", {"summary": summary}, audit_id)
    else:
        db.save("reports", {
            "audit_id": audit_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "analysis": json.dumps(analysis),
            "formal_report": formal_report,
            "summary": summary
        })

    return {"audit_id": audit_id, "summary": summary}