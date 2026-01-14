from openai import OpenAI
from datetime import datetime
from . import config

client = OpenAI()

SYSTEM_PROMPT = (
    "You are an AI meeting assistant.\n"
    "Summarize the meeting in a clear, concise, and professional manner.\n"
    "Focus on the main discussion points, objectives, and outcomes.\n"
    "Do NOT include action items, decisions, or risks.\n"
    "Write in neutral, executive-friendly language.\n" 
    "Limit the summary to 5–7 bullet points or a short paragraph."
)

def summarize_meeting(meeting_id: str, transcript: str) -> dict:
    response = client.chat.completions.create(
        model=config.MODEL_NAME,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": transcript},
        ],
        temperature=config.TEMPERATURE_SUMMARY,
        max_tokens=config.MAX_TOKENS_SUMMARY,
    )

    return {
        "meeting_id": meeting_id,
        "summary": response.choices[0].message.content,
        "created_at": datetime.utcnow().isoformat(),
    }
