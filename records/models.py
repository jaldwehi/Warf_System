from django.db import models
from django.conf import settings


class Record(models.Model):
    meeting = models.OneToOneField(
        "meetings.Meeting",
        on_delete=models.CASCADE,
        related_name="recording"
    )

    file = models.FileField(upload_to="recordings/", null=True, blank=True)
    transcript = models.TextField(blank=True)  # لاحقًا نخزن التفريغ هنا

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_recordings"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Recording for {self.meeting}"


# =========================
# WARF Assistant Knowledge
# =========================

class KnowledgeDocument(models.Model):
    DOC_TYPES = [
        ("seed_knowledge", "Seed Knowledge"),
        ("transcript", "Transcript"),
        ("minutes", "Minutes"),
        ("decision", "Decision"),
        ("task", "Task"),
        ("policy", "Policy"),
    ]

    VISIBILITY_CHOICES = [
        ("public", "Public"),
        ("internal", "Internal"),
        ("confidential", "Confidential"),
    ]

    title = models.CharField(max_length=255)
    doc_type = models.CharField(max_length=50, choices=DOC_TYPES, default="seed_knowledge")
    content = models.TextField()

    # ربط اختياري بميتنق (بدون ما نعتمد على Meeting FK حتى لو الداتا مو من نظامك)
    external_meeting_id = models.CharField(max_length=64, blank=True, null=True)

    # Metadata للفلترة + الصلاحيات + التتبع
    metadata = models.JSONField(default=dict, blank=True)

    visibility = models.CharField(max_length=30, choices=VISIBILITY_CHOICES, default="internal")

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name="knowledge_documents"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.doc_type})"


class KnowledgeChunk(models.Model):
    document = models.ForeignKey(KnowledgeDocument, on_delete=models.CASCADE, related_name="chunks")
    chunk_index = models.PositiveIntegerField()
    text = models.TextField()

    # نخليه اختياري الآن (نفعّله لاحقًا لما نضيف embeddings)
    embedding = models.JSONField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("document", "chunk_index")

    def __str__(self):
        return f"Chunk {self.chunk_index} - Doc {self.document_id}"
