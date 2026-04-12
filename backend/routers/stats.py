from fastapi import APIRouter, Request, HTTPException
from backend.stats import calculate_all_stats, calculate_dimension_stats, filter_by_period

router = APIRouter(prefix="/stats", tags=["Stats"])


@router.get("/{audit_id}/{dimension}")
async def get_dimension_stats(audit_id: str, dimension: str, request: Request, period: str = "all_time"):
    db = request.app.state.db
    config = request.app.state.config

    # Validate dimension against config
    valid_dimensions = config["audit_dimensions"]
    if dimension not in valid_dimensions:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid dimension '{dimension}'. Valid options: {valid_dimensions}"
        )

    if audit_id == "all":
        records = db.get_all("applications")
    else:
        records = db.get_all("applications", audit_id)

    if not records:
        raise HTTPException(status_code=404, detail="No data found")

    records = filter_by_period(records, period)
    rows = calculate_dimension_stats(records, dimension, config)

    return {
        "audit_id": audit_id,
        "dimension": dimension,
        "available_dimensions": valid_dimensions,
        "rows": rows
    }


@router.get("/all/summary")
async def get_all_summary(request: Request):
    db = request.app.state.db
    config = request.app.state.config

    records = db.get_all("applications")
    if not records:
        raise HTTPException(status_code=404, detail="No data found")

    dimensions = config["audit_dimensions"]
    result = {}
    for dimension in dimensions:
        result[dimension] = calculate_dimension_stats(records, dimension, config)

    return {
        "audit_id": "all",
        "dimensions": dimensions,
        "stats": result
    }