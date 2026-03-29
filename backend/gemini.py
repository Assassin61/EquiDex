import httpx
import os
import json


GEMINI_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


async def call_gemini(prompt: str, system_instruction: str = None) -> str:
    """
    Calls Gemini API with a prompt.
    Returns the text response.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        raise ValueError("GEMINI_API_KEY not found in environment variables")
    
    # Build request body
    body = {
        "contents": [
            {
                "parts": [{"text": prompt}]
            }
        ]
    }
    
    # Add system instruction if provided
    if system_instruction:
        body["system_instruction"] = {
            "parts": [{"text": system_instruction}]
        }
    
    async with httpx.AsyncClient(timeout=30) as client:
        response = await client.post(
            f"{GEMINI_URL}?key={api_key}",
            json=body
        )
        
        if response.status_code != 200:
            raise Exception(f"Gemini API error: {response.text}")
        
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]


async def analyse_bias(stats: dict, config: dict) -> dict:
    """
    Sends pre-calculated stats to Gemini for bias interpretation.
    Gemini never generates numbers — only interprets them.
    """
    domain = config["reporting"]["domain"]
    jurisdiction = config["reporting"]["jurisdiction"]
    
    system_instruction = """
    You are an AI fairness expert and compliance analyst.
    You analyze hiring statistics for bias and discrimination.
    You never generate or estimate statistics yourself.
    You only interpret the exact numbers provided to you.
    Always respond with valid JSON only. No markdown. No explanation outside JSON.
    """
    
    prompt = f"""
    Analyze these hiring statistics for bias and discrimination.
    Domain: {domain}
    Jurisdiction: {jurisdiction}
    
    Statistics provided:
    {json.dumps(stats, indent=2)}
    
    Return ONLY this JSON structure:
    {{
        "bias_detected": true or false,
        "summary": "one paragraph plain English summary",
        "findings": [
            {{
                "dimension": "dimension name",
                "severity": "HIGH or MEDIUM or LOW",
                "evidence": "one sentence using only the provided numbers",
                "affected_group": "which group is disadvantaged"
            }}
        ],
        "overall_severity": "HIGH or MEDIUM or LOW or NONE"
    }}
    """
    
    response = await call_gemini(prompt, system_instruction)
    
    # Clean response and parse JSON
    clean = response.strip()
    if clean.startswith("```"):
        clean = clean.split("```")[1]
        if clean.startswith("json"):
            clean = clean[4:]
    
    return json.loads(clean.strip())


async def generate_report(analysis: dict, stats: dict, config: dict) -> str:
    """
    Generates a formal compliance report from bias analysis.
    """
    domain = config["reporting"]["domain"]
    jurisdiction = config["reporting"]["jurisdiction"]
    company = config["company"]
    
    # Hardcoded legal references — never let Gemini invent laws
    legal_references = {
        "employment": [
            "Title VII of the Civil Rights Act of 1964",
            "Age Discrimination in Employment Act of 1967",
            "Equal Employment Opportunity Commission Guidelines"
        ],
        "banking": [
            "Equal Credit Opportunity Act",
            "Fair Housing Act",
            "Community Reinvestment Act"
        ],
        "healthcare": [
            "Section 1557 of the Affordable Care Act",
            "Americans with Disabilities Act"
        ]
    }
    
    laws = legal_references.get(domain, [])
    
    system_instruction = """
    You are a compliance report writer specializing in AI bias documentation.
    Write formal, professional reports based only on provided data.
    Never invent statistics or legal references not provided to you.
    """
    
    prompt = f"""
    Write a formal AI bias audit compliance report.
    
    Company: {company}
    Domain: {domain}
    Jurisdiction: {jurisdiction}
    
    Bias Analysis Results:
    {json.dumps(analysis, indent=2)}
    
    Overall Statistics:
    {json.dumps(stats.get("overall", {}), indent=2)}
    
    Applicable Laws (use only these, do not add others):
    {json.dumps(laws, indent=2)}
    
    Write a professional compliance report with these sections:
    1. Executive Summary
    2. Audit Methodology
    3. Key Findings
    4. Legal Exposure
    5. Remediation Recommendations
    6. Next Steps
    
    Keep it professional but accessible. Under 500 words total.
    """
    
    return await call_gemini(prompt, system_instruction)


async def summarize_report(report: str) -> str:
    """
    Summarizes a formal report into plain English.
    For non-technical executives.
    """
    system_instruction = """
    You are a plain language expert.
    You convert technical compliance reports into simple English.
    Anyone should be able to understand your summaries.
    Maximum 150 words. No jargon.
    """
    
    prompt = f"""
    Summarize this compliance report in plain English.
    Maximum 150 words. No technical jargon.
    
    Report:
    {report}
    """
    
    return await call_gemini(prompt, system_instruction)