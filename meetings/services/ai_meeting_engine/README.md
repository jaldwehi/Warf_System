# AI Meeting Engine

## Description
AI service that processes meeting transcripts and returns:
- Meeting summary
- Decisions
- Action items
- Risks
- Notes

## Input
POST /api/meeting/process

```json
{
  "meeting_id": "meeting_001",
  "transcript": "Full meeting transcript here..."
}
