import os
import json
from pathlib import Path


def _load_prompt(name: str) -> str:
    """Load prompt from prompts directory, return empty string if file is empty."""
    safe_name = os.path.basename(name)
    prompt_path = Path(__file__).parent / "prompts" / f"{safe_name}.txt"
    if prompt_path.exists():
        content = prompt_path.read_text().strip()
        if content:
            return content
    return ""


def call_groq(prompt: str, system: str = None) -> str:
    """Call Groq API with the configured model."""
    from groq import Groq
    
    api_key = os.getenv("GROQ_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError(
            "GROQ_API_KEY is not set. "
            "Create a .env file in the project root with: GROQ_API_KEY=your_key_here  "
            "Get a free key at https://console.groq.com/keys"
        )
        
    client = Groq(api_key=api_key)
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=messages,
        temperature=0.3,
        max_tokens=2000
    )
    return response.choices[0].message.content


async def call_gemini(prompt: str, system: str = None) -> str:
    """Call Google Gemini API with the configured model."""
    import google.generativeai as genai
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=system
    )
    response = model.generate_content(prompt)
    return response.text


def call_ollama(prompt: str, config: dict, system: str = None) -> str:
    """Call a local Ollama model."""
    import httpx
    
    model_name = config.get("ai", {}).get("model", "llama3.1")
    url = "http://localhost:11434/api/chat"
    
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_name,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": 0.3
        }
    }
    
    try:
        # Use a longer timeout for local models since they can be slow to generate/load
        with httpx.Client(timeout=120.0) as client:
            response = client.post(url, json=payload)
            response.raise_for_status()
            data = response.json()
            return data["message"]["content"]
    except Exception as e:
        raise RuntimeError(f"Failed to connect to local Ollama (is it running?): {str(e)}")


def call_ai(prompt: str, config: dict, system: str = None) -> str:
    """
    Config-driven AI call. Routes to Groq, Gemini, or Ollama
    based on config['ai']['provider'].
    """
    provider = config.get("ai", {}).get("provider", "gemini")

    if provider == "ollama":
        return call_ollama(prompt, config, system)
    elif provider == "gemini":
        import google.generativeai as genai

        api_key = os.getenv("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not set. "
                "Create a .env file in the project root with: GEMINI_API_KEY=your_key_here  "
                "Get a free key at https://aistudio.google.com/app/apikey"
            )

        genai.configure(api_key=api_key)

        model_name = config.get("ai", {}).get("model", "gemini-2.5-flash")
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=system
        )
        response = model.generate_content(prompt)
        return response.text
    else:
        return call_groq(prompt, system)


async def analyse_bias(stats: dict, config: dict) -> dict:
    domain = config["reporting"]["domain"]
    jurisdiction = config["reporting"]["jurisdiction"]

    system = """You are an AI fairness expert and compliance analyst.
You analyze hiring statistics for bias and discrimination.
You never generate or estimate statistics yourself.
You only interpret the exact numbers provided to you.
Always respond with valid JSON only. No markdown. No explanation outside JSON."""

    prompt = f"""Analyze these hiring statistics for bias and discrimination.
Domain: {domain}
Jurisdiction: {jurisdiction}

Statistics provided:
{json.dumps(stats, indent=2)}

Return ONLY this JSON structure, no markdown, no backticks:
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
}}"""

    response = call_ai(prompt, config, system)

    clean = response.strip()
    if clean.startswith("```"):
        clean = clean[clean.index("{"):]
    if clean.endswith("```"):
        clean = clean[:clean.rindex("}") + 1]

    return json.loads(clean.strip())


async def generate_report(analysis: dict, stats: dict, config: dict) -> str:
    domain = config["reporting"]["domain"]
    jurisdiction = config["reporting"]["jurisdiction"]
    company = config["company"]

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

    system = """You are a compliance report writer specializing in AI bias documentation.
Write formal, professional reports based only on provided data.
Never invent statistics or legal references not provided to you."""

    prompt = f"""Write a formal AI bias audit compliance report.

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

Keep it professional but accessible. Under 500 words total."""

    return call_ai(prompt, config, system)


async def summarize_report(report: str, config: dict = None) -> str:
    system = """You are a plain language expert.
You convert technical compliance reports into simple English.
Anyone should be able to understand your summaries.
Maximum 150 words. No jargon."""

    prompt = f"""Summarize this compliance report in plain English.
Maximum 150 words. No technical jargon.

Report:
{report}"""

    if config:
        return call_ai(prompt, config, system)
    else:
        # Fallback to Gemini if no config provided
        return call_ai(prompt, {}, system)