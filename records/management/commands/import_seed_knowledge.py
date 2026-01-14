import json
from django.core.management.base import BaseCommand
from records.models import KnowledgeDocument, KnowledgeChunk


def safe_str(value):
    """
    يحول أي قيمة (None / رقم / نص) إلى نص آمن
    """
    if value is None:
        return ""
    return str(value).strip()


def chunk_text(text: str, max_words: int = 700, overlap: int = 120):
    """
    تقطيع النص إلى chunks مناسبة للـ RAG
    """
    words = (text or "").split()
    if not words:
        return []

    chunks = []
    step = max_words - overlap
    if step <= 0:
        step = max_words

    i = 0
    while i < len(words):
        chunk = words[i:i + max_words]
        chunks.append(" ".join(chunk))
        i += step

    return chunks


class Command(BaseCommand):
    help = "Import JSONL seed knowledge into KnowledgeDocument and KnowledgeChunk"

    def add_arguments(self, parser):
        parser.add_argument("jsonl_path", type=str, help="Path to JSONL file")
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete existing seed_knowledge before import"
        )

    def handle(self, *args, **options):
        path = options["jsonl_path"]
        clear = options["clear"]

        if clear:
            KnowledgeChunk.objects.filter(document__doc_type="seed_knowledge").delete()
            KnowledgeDocument.objects.filter(doc_type="seed_knowledge").delete()
            self.stdout.write(self.style.WARNING("Existing seed_knowledge cleared"))

        created_docs = 0
        created_chunks = 0

        with open(path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, start=1):
                line = line.strip()
                if not line:
                    continue

                try:
                    row = json.loads(line)
                except json.JSONDecodeError:
                    self.stdout.write(
                        self.style.ERROR(f"Invalid JSON at line {line_num}")
                    )
                    continue

                meeting_id = safe_str(row.get("meeting_id")) or f"seed-{line_num}"
                data = row.get("decision_data") or {}

                problem = safe_str(data.get("problem"))
                decision = safe_str(data.get("decision"))
                justification = safe_str(data.get("justification"))
                confidence = safe_str(data.get("confidence"))

                options_list = data.get("options") or []
                if not isinstance(options_list, list):
                    options_list = [options_list]

                tasks_list = data.get("tasks") or []
                if not isinstance(tasks_list, list):
                    tasks_list = []

                options_text = "\n".join(
                    [f"- {safe_str(o)}" for o in options_list]
                ) if options_list else "- (none)"

                tasks_text = "\n".join([
                    f"- {safe_str(t.get('task'))} | "
                    f"owner: {safe_str(t.get('owner'))} | "
                    f"due: {safe_str(t.get('deadline'))} | "
                    f"priority: {safe_str(t.get('priority'))}"
                    for t in tasks_list if isinstance(t, dict)
                ]) if tasks_list else "- (none)"

                content = f"""SEED KNOWLEDGE (Meeting ID: {meeting_id})

PROBLEM:
{problem or "(empty)"}

OPTIONS:
{options_text}

DECISION:
{decision or "(empty)"}

JUSTIFICATION:
{justification or "(empty)"}

CONFIDENCE:
{confidence or "(empty)"}

TASKS:
{tasks_text}
"""

                doc = KnowledgeDocument.objects.create(
                    title=f"Seed Meeting Knowledge - {meeting_id}",
                    doc_type="seed_knowledge",
                    content=content,
                    external_meeting_id=meeting_id,
                    metadata={
                        "source": "seed_data_jsonl",
                        "confidence": confidence,
                        "line": line_num,
                    },
                    visibility="internal",
                )
                created_docs += 1

                chunks = chunk_text(content, max_words=700, overlap=120)
                for idx, ch in enumerate(chunks):
                    KnowledgeChunk.objects.create(
                        document=doc,
                        chunk_index=idx,
                        text=ch
                    )
                    created_chunks += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"Import completed successfully ✅ "
                f"(Documents: {created_docs}, Chunks: {created_chunks})"
            )
        )
