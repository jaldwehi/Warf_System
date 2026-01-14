from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Meeting(models.Model):
    MODE_CHOICES = [
        ("online", "Online Meeting"),
        ("upload", "Upload Meeting"),
        ("both", "Online + Upload"),
    ]

    title = models.CharField(max_length=200)

    # legacy (keep to avoid breaking old data/pages)
    scheduled_at = models.DateTimeField()

    # official timing
    starts_at = models.DateTimeField(null=True, blank=True)
    ends_at = models.DateTimeField(null=True, blank=True)

    # time window policy
    join_early_minutes = models.PositiveIntegerField(default=10)
    join_late_minutes = models.PositiveIntegerField(default=30)

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="organized_meetings",
    )

    location = models.CharField(max_length=255, blank=True)
    agenda = models.TextField(blank=True)

    # upload transcript (for upload mode)
    transcript_text = models.TextField(blank=True, default="")
    transcript_uploaded_at = models.DateTimeField(null=True, blank=True)


    # meeting mode: online/upload/both
    mode = models.CharField(max_length=10, choices=MODE_CHOICES, default="online")

    # ---------------------------
    # Jitsi fields
    # ---------------------------
    jitsi_room = models.CharField(max_length=255, unique=True, blank=True)
    jitsi_domain = models.CharField(max_length=255, blank=True, default="")

    require_face_verification = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # auto room
        if not self.jitsi_room:
            self.jitsi_room = f"warF-{uuid.uuid4().hex[:10]}"

        # backfill starts_at from scheduled_at if missing
        if self.scheduled_at and not self.starts_at:
            self.starts_at = self.scheduled_at

        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    def is_open_now(self):
        """
        Meeting room access policy:
        - allow entering from (starts_at - join_early_minutes) until (ends_at + join_late_minutes)
        - if ends_at is not set, fallback to starts_at window (starts_at..starts_at+2h)
        """
        if not self.starts_at:
            return False

        start = self.starts_at - timezone.timedelta(minutes=self.join_early_minutes)

        if self.ends_at:
            end = self.ends_at + timezone.timedelta(minutes=self.join_late_minutes)
        else:
            # fallback: assume 2 hours duration
            end = self.starts_at + timezone.timedelta(hours=2) + timezone.timedelta(minutes=self.join_late_minutes)

        now = timezone.now()
        return start <= now <= end

    def open_status_message(self):
        if not self.starts_at:
            return "Meeting time is not configured."

        now = timezone.now()
        open_from = self.starts_at - timezone.timedelta(minutes=self.join_early_minutes)

        if self.ends_at:
            close_at = self.ends_at + timezone.timedelta(minutes=self.join_late_minutes)
        else:
            close_at = self.starts_at + timezone.timedelta(hours=2) + timezone.timedelta(minutes=self.join_late_minutes)

        if now < open_from:
            return f"Meeting is not open yet. Opens at {open_from:%Y-%m-%d %H:%M}."
        if now > close_at:
            return f"Meeting has ended. Closed at {close_at:%Y-%m-%d %H:%M}."
        return "Meeting is open."
    

class Attendee(models.Model):
    ROLE_CHOICES = [
        ("host", "Host"),
        ("member", "Member"),
        ("guest", "Guest"),
    ]

    meeting = models.ForeignKey(
        Meeting,
        on_delete=models.CASCADE,
        related_name="attendees",
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="meeting_attendances",
    )

    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default="member")

    face_verified = models.BooleanField(default=False)
    face_verified_at = models.DateTimeField(null=True, blank=True)

    confidence = models.FloatField(null=True, blank=True)

    joined_at = models.DateTimeField(null=True, blank=True)
    left_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ("meeting", "user")

    def __str__(self):
        return f"{self.user} ({self.role}) @ {self.meeting}"
