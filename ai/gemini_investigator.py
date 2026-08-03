import json
import os

from dotenv import load_dotenv
from google import genai

from ai.investigator import run_investigation

load_dotenv()

api_key = os.getenv("GEMINI_API_KEY")
model = os.getenv("GEMINI_MODEL")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env")

client = genai.Client(api_key=api_key)


def generate_ai_report():

    investigation = run_investigation()

    prompt = f"""
You are a Senior Production Support Engineer.

Analyze the following incident investigation.

Return a professional Root Cause Analysis.

Include:

1. Incident Summary

2. Root Cause

3. Evidence

4. Business Impact

5. Immediate Resolution

6. Preventive Actions

7. Confidence Score Explanation

Incident Data

{json.dumps(investigation, indent=4)}
"""

    response = client.models.generate_content(
        model=model,
        contents=prompt
    )

    return response.text


if __name__ == "__main__":

    report = generate_ai_report()

    print(report)