from typing import Dict, Any

def run_ai(meeting_id: str, minutes_text: str) -> Dict[str, Any]:
    """
    WARF unified AI interface
    """

    minutes_text = (minutes_text or "").strip()
    if not minutes_text:
        return {"summary": "", "decisions": []}

    from .pipeline import run_pipeline

    result = run_pipeline(
        meeting_id=str(meeting_id),
        transcript=minutes_text
    )

    return {
        "summary": result.get("summary", ""),
        "decisions": result.get("decisions", []),
    }
