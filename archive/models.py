from django.db import models
from django.conf import settings


class ArchiveEntry(models.Model):
    """
    Company Memory:
    A unified archive record that can reference:
    - Task solutions
    - Approved minutes & decisions
    - General attachments
    """

    TYPE_CHOICES = [
        ("solution", "Solution"),
        ("minutes", "Minutes & Decisions"),
        ("attachment", "Attachment"),
    ]

    type = models.CharField(max_length=20, choices=TYPE_CHOICES)

    # Human-friendly info
    title = models.CharField(max_length=255)
    summary = models.TextField(blank=True)

    # Optional file (for attachments/solutions)
    file = models.FileField(upload_to="archive/", null=True, blank=True)

    # Who produced this knowledge (employee/admin)
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archive_entries",
    )

    # References (we link, not duplicate)
    meeting = models.ForeignKey(
        "meetings.Meeting",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archive_entries",
    )

    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archive_entries",
    )

    minutes = models.ForeignKey(
        "minutes.Minutes",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="archive_entries",
    )

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.get_type_display()} — {self.title}"
