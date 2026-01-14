import json
from openai import OpenAI
from . import config

client = OpenAI()

JSON_SCHEMA_HINT = """
Return ONLY valid JSON (no markdown, no code fences).
Schema:
{
  "decisions": [string],
  "action_items": [
    { "title": string, "assignee": string|null, "due_date": string|null, "priority": "low"|"medium"|"high" }
  ],
  "risks": [string],
  "notes": [string]
}
Rules:
- If assignee not mentioned, use null.
- If due date not mentioned, use null.
- Keep items short and actionable.
"""

def extract_decisions(meeting_id: str, transcript: str) -> dict:
    prompt = f"""{JSON_SCHEMA_HINT}

Meeting ID: {meeting_id}

Transcript:
{transcript}
"""

    resp = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": "You extract structured decisions and action items from meeting transcripts."},
            {"role": "user", "content": prompt},
        ],
        temperature=config.TEMPERATURE_DECISIONS,
        max_tokens=config.MAX_TOKENS_DECISIONS,
    )

    content = resp.choices[0].message.content.strip()

    # Defensive JSON parsing
    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        # fallback: wrap raw text
        data = {
            "decisions": [],
            "action_items": [],
            "risks": [],
            "notes": [],
            "_raw": content
        }

    return {"meeting_id": meeting_id, "output": data}

