from django.db import models
from django.conf import settings
from django.utils import timezone


class Minutes(models.Model):
    """
    WARF Minutes
    - One minutes record per meeting (OneToOne)
    - Supports lifecycle: draft -> review -> approved
    - Stores both manual minutes and AI outputs (summary/decisions)
    """

    STATUS_DRAFT = "draft"
    STATUS_REVIEW = "review"
    STATUS_APPROVED = "approved"

    STATUS_CHOICES = [
        (STATUS_DRAFT, "Draft"),
        (STATUS_REVIEW, "Under Review"),
        (STATUS_APPROVED, "Approved"),
    ]

    meeting = models.OneToOneField(
        "meetings.Meeting",
        on_delete=models.CASCADE,
        related_name="minutes",
        db_index=True,
    )

    # Manual minutes
    discussion_points = models.TextField(blank=True, default="")
    summary = models.TextField(blank=True, default="")

    # AI outputs (kept here for the WARF "single source of truth")
    ai_summary = models.TextField(blank=True, default="")
    ai_decisions = models.TextField(blank=True, default="")
    ai_generated_at = models.DateTimeField(null=True, blank=True)

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        db_index=True,
    )

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="created_minutes",
    )

    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="approved_minutes",
    )
    approved_at = models.DateTimeField(null=True, blank=True)

    # Lock minutes after approval (prevents accidental edits)
    is_locked = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]
        verbose_name = "Minutes"
        verbose_name_plural = "Minutes"

    def __str__(self):
        # Display name in admin/listing: meeting title if exists
        title = getattr(self.meeting, "title", str(self.meeting))
        return f"Minutes — {title}"

    @property
    def meeting_title(self):
        return getattr(self.meeting, "title", "Meeting")

    def approve(self, user):
        """Approve minutes and lock them."""
        if self.status == self.STATUS_APPROVED:
            return  # already approved

        self.status = self.STATUS_APPROVED
        self.approved_by = user
        self.approved_at = timezone.now()
        self.is_locked = True
        self.save(update_fields=["status", "approved_by", "approved_at", "is_locked"])

    def send_to_review(self):
        """Move minutes from draft to review (no lock yet)."""
        if self.status == self.STATUS_APPROVED:
            return
        self.status = self.STATUS_REVIEW
        self.save(update_fields=["status"])

    def unlock(self):
        """Admin-only usage (we’ll enforce in views): allow edits after approval if needed."""
        self.is_locked = False
        self.save(update_fields=["is_locked"])


class AIOutput(models.Model):
    """
    Optional: keep structured AI output for the meeting.
    We keep it because:
    - JSON structure is useful for decisions/tasks extraction
    - But Minutes remains the primary view layer (human-readable)
    """

    meeting = models.OneToOneField(
        "meetings.Meeting",
        on_delete=models.CASCADE,
        related_name="ai_output",
        db_index=True,
    )

    summary_text = models.TextField(blank=True, default="")
    decisions_json = models.JSONField(default=dict, blank=True)  # decisions/action_items/risks/notes

    model_name = models.CharField(max_length=100, blank=True, default="")
    pipeline_version = models.CharField(max_length=30, blank=True, default="v1")

    generated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-generated_at"]
        verbose_name = "AI Output"
        verbose_name_plural = "AI Outputs"

    def __str__(self):
        title = getattr(self.meeting, "title", str(self.meeting))
        return f"AI Output — {title}"
