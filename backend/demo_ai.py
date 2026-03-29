from backend.config import load_config

def evaluate_candidate(candidate: dict, config: dict) -> dict:
    """
    Demo hiring AI with hidden bias baked in.
    Scores candidates on legitimate factors
    but secretly penalizes certain names and ages.
    
    In real deployment this is replaced by
    the company's actual AI system.
    """
    demo_settings = config["demo"]
    score = 0

    # Legitimate scoring
    score += candidate.get("experience", 0) * 10
    score += candidate.get("gpa", 0) * 20

    # Hidden bias — name discrimination
    biased_names = demo_settings["biased_names"]
    candidate_name = candidate.get("name", "")
    
    if any(name.lower() in candidate_name.lower() for name in biased_names):
        score -= demo_settings["name_bias_penalty"]

    # Hidden bias — age discrimination
    age = candidate.get("age", 0)
    if age > demo_settings["age_bias_threshold"]:
        score -= demo_settings["age_bias_penalty"]

    # Final decision
    decision = "accepted" if score > 60 else "rejected"

    return {
        "decision": decision,
        "score": score,
        "candidate": candidate
    }


def run_batch(candidates: list, config: dict) -> list:
    """
    Runs all candidates through the demo hiring AI.
    Returns list of decisions.
    """
    results = []
    
    for candidate in candidates:
        result = evaluate_candidate(candidate, config)
        results.append(result)
    
    return results