import json
import os
import time

from dotenv import load_dotenv
from google import genai
from openai import max_retries
from pydantic import BaseModel

from ai.investigator import run_investigation

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


class IncidentReport(BaseModel):
    root_cause: str
    root_cause_reasoning: str
    business_impact: str
    impact_severity: str  # "low" | "medium" | "high" | "critical"
    confidence_score: int  # 0-100, inferred by the model
    confidence_reasoning: str
    immediate_resolution: str
    preventive_actions: list[str]


def generate_ai_report(max_retries: int = 3) -> dict:
    investigation = run_investigation()

    prompt = f"""
You are a Senior Production Support Engineer investigating a production incident
in an ecommerce order system.

You are given raw evidence only — no conclusions. Determine the root cause,
business impact, and your own confidence based strictly on this evidence.

Confidence scoring rubric (0-100):
- 90-100: evidence directly and unambiguously identifies the cause
- 60-89: evidence strongly suggests a cause but some details are inferred
- 30-59: evidence is suggestive but multiple explanations remain plausible
- 0-29: evidence is too sparse or ambiguous to draw a real conclusion

Impact severity should weigh: revenue_at_risk, unique_customers_affected,
and whether the failure is user-facing (blocks checkout) vs. internal.

Evidence:
{json.dumps(investigation["evidence"], indent=2)}

Documentation excerpt (may or may not be relevant — judge for yourself):
{investigation["documentation_content"][:2000]}
"""
    last_error = None
    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": IncidentReport,
                },
            )
            report = IncidentReport.model_validate_json(response.text)
            return report.model_dump()

        except Exception as error:
            last_error = error
            print(f"Attempt {attempt + 1} failed: {type(error).__name__}: {error}")
            wait_time = 2 ** attempt
            time.sleep(wait_time)
    raise last_error

    response = client.models.generate_content(
        model=model,
        contents=prompt,
        config={
            "response_mime_type": "application/json",
            "response_schema": IncidentReport,
        },
    )

    report = IncidentReport.model_validate_json(response.text)
    return report.model_dump()


if __name__ == "__main__":
    report = generate_ai_report()
    print(json.dumps(report, indent=2))











# import json
# import os

# from dotenv import load_dotenv
# from google import genai

# from ai.investigator import run_investigation

# load_dotenv()

# api_key = os.getenv("GEMINI_API_KEY")
# model = os.getenv("GEMINI_MODEL")

# if not api_key:
#     raise ValueError("GEMINI_API_KEY not found in .env")

# client = genai.Client(api_key=api_key)


# def generate_ai_report():

#     investigation = run_investigation()

#     prompt = f"""
# You are a Senior Production Support Engineer.

# Analyze the following incident investigation.

# Return a professional Root Cause Analysis.

# Include:

# 1. Incident Summary

# 2. Root Cause

# 3. Evidence

# 4. Business Impact

# 5. Immediate Resolution

# 6. Preventive Actions

# 7. Confidence Score Explanation

# Incident Data

# {json.dumps(investigation, indent=4)}
# """

#     response = client.models.generate_content(
#         model=model,
#         contents=prompt
#     )

#     return response.text


# if __name__ == "__main__":

#     report = generate_ai_report()

#     print(report)