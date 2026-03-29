from datetime import datetime, timedelta


def get_age_group(age: int) -> str:
    """Converts age to age group label."""
    if age < 30:
        return "22-29"
    elif age < 40:
        return "30-39"
    elif age < 50:
        return "40-49"
    else:
        return "50+"


def get_name_origin(name: str, config: dict) -> str:
    """
    Classifies name origin based on biased names list.
    In production this would use a proper name origin classifier.
    """
    biased_names = config["demo"]["biased_names"]
    if any(n.lower() in name.lower() for n in biased_names):
        return "Non-Western"
    return "Western"


def calculate_overall_stats(records: list) -> dict:
    """
    Calculates general statistics across all records.
    """
    total = len(records)
    if total == 0:
        return {}

    accepted = len([r for r in records if r["decision"] == "accepted"])
    rejected = total - accepted

    return {
        "total_applications": total,
        "total_accepted": accepted,
        "total_rejected": rejected,
        "acceptance_rate": round(accepted / total * 100, 1)
    }


def calculate_dimension_stats(records: list, dimension: str, config: dict) -> list:
    """
    Groups records by a dimension and calculates
    acceptance rates per group.
    Returns list of rows for the dashboard table.
    """
    groups = {}
    overall_rate = calculate_overall_stats(records).get("acceptance_rate", 0)

    for record in records:
        # Get group label based on dimension
        if dimension == "name_origin":
            group = get_name_origin(record.get("name", ""), config)
        elif dimension == "age_group":
            group = get_age_group(record.get("age", 0))
        elif dimension == "ethnicity":
            group = record.get("ethnicity", "Unknown")
        else:
            group = record.get(dimension, "Unknown")

        if group not in groups:
            groups[group] = {"total": 0, "accepted": 0}

        groups[group]["total"] += 1
        if record["decision"] == "accepted":
            groups[group]["accepted"] += 1

    # Build result rows
    rows = []
    for group, data in groups.items():
        total = data["total"]
        accepted = data["accepted"]
        rate = round(accepted / total * 100, 1) if total > 0 else 0
        vs_average = round(rate - overall_rate, 1)

        # Determine bias severity
        disparity = abs(vs_average)
        if disparity >= config["thresholds"]["high_bias"]:
            severity = "HIGH"
        elif disparity >= config["thresholds"]["medium_bias"]:
            severity = "MEDIUM"
        else:
            severity = "LOW"

        rows.append({
            "group": group,
            "total": total,
            "accepted": accepted,
            "acceptance_rate": rate,
            "vs_average": vs_average,
            "severity": severity
        })

    # Sort by acceptance rate ascending
    rows.sort(key=lambda x: x["acceptance_rate"])
    return rows


def calculate_all_stats(records: list, config: dict) -> dict:
    """
    Calculates stats for all dimensions defined in config.
    This is what FastAPI sends to the dashboard.
    """
    dimensions = config["audit_dimensions"]
    stats = {
        "overall": calculate_overall_stats(records),
        "dimensions": {}
    }

    for dimension in dimensions:
        stats["dimensions"][dimension] = calculate_dimension_stats(
            records, dimension, config
        )

    return stats


def filter_by_period(records: list, period: str) -> list:
    """
    Filters records by time period.
    """
    if period == "all_time" or not period:
        return records

    periods = {
        "last_week": timedelta(days=7),
        "last_month": timedelta(days=30),
        "last_3months": timedelta(days=90),
        "last_year": timedelta(days=365)
    }

    if period not in periods:
        return records

    cutoff = datetime.now() - periods[period]

    filtered = []
    for record in records:
        try:
            ts = datetime.fromisoformat(record["timestamp"])
            if ts >= cutoff:
                filtered.append(record)
        except (ValueError, TypeError):
            filtered.append(record)

    return filtered