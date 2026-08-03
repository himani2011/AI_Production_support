import json
import os

from dotenv import load_dotenv
from openai import OpenAI

from ai.investigator import run_investigation


load_dotenv()

api_key = os.getenv("OPENAI_API_KEY")
model_name = os.getenv("OPENAI_MODEL")

if not api_key:
    raise ValueError(
        "OPENAI_API_KEY is missing from the .env file."
    )

if not model_name:
    raise ValueError(
        "OPENAI_MODEL is missing from the .env file."
    )

client = OpenAI(api_key=api_key)


def generate_ai_report() -> str:
    evidence = run_investigation()

    prompt = f"""
You are a production-support engineer.

Analyze the incident evidence below.

Use only the supplied evidence. Do not invent services,
events, database findings, or technical causes.

Return a clear report containing:

1. Incident summary
2. Most likely root cause
3. Evidence
4. Business impact
5. Recommended immediate actions
6. Preventive actions
7. Confidence explanation

Incident evidence:

{json.dumps(evidence, indent=2)}
"""

    response = client.responses.create(
        model=model_name,
        input=prompt,
    )

    return response.output_text


if __name__ == "__main__":
    print(generate_ai_report())