from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Meeting

User = get_user_model()


class MeetingCreateForm(forms.ModelForm):
    attendees = forms.ModelMultipleChoiceField(
        queryset=User.objects.all().order_by("username"),
        required=False,
        widget=forms.SelectMultiple(attrs={"class": "form-select", "size": "8"}),
        help_text="Select attendees (users). The organizer will be added automatically as Host."
    )

    class Meta:
        model = Meeting
        fields = [
            "title",
            "mode",
            "starts_at",
            "ends_at",
            "location",
            "agenda",
            "jitsi_domain",
            "require_face_verification",
            "join_early_minutes",
            "join_late_minutes",
        ]
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "e.g., Weekly Sync"}),
            "mode": forms.Select(attrs={"class": "form-select"}),
            "starts_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "ends_at": forms.DateTimeInput(attrs={"class": "form-control", "type": "datetime-local"}),
            "location": forms.TextInput(attrs={"class": "form-control", "placeholder": "Optional"}),
            "agenda": forms.Textarea(attrs={"class": "form-control", "rows": 4, "placeholder": "Optional agenda..."}),
            "jitsi_domain": forms.TextInput(attrs={"class": "form-control", "placeholder": "meet.jit.si or your domain"}),
            "require_face_verification": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "join_early_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 120}),
            "join_late_minutes": forms.NumberInput(attrs={"class": "form-control", "min": 0, "max": 240}),
        }

    def clean_jitsi_domain(self):
        domain = (self.cleaned_data.get("jitsi_domain") or "").strip()

        # allow blank (we will enforce only when mode needs online)
        if not domain:
            return ""

        # normalize: remove scheme and trailing slashes
        domain = domain.replace("https://", "").replace("http://", "")
        domain = domain.strip().strip("/")

        # basic sanity
        if " " in domain or "/" in domain:
            raise forms.ValidationError("Enter a valid domain like: meet.jit.si")

        return domain

    def clean(self):
        cleaned = super().clean()

        title = (cleaned.get("title") or "").strip()
        mode = cleaned.get("mode")
        starts_at = cleaned.get("starts_at")
        ends_at = cleaned.get("ends_at")
        early = cleaned.get("join_early_minutes")
        late = cleaned.get("join_late_minutes")
        domain = (cleaned.get("jitsi_domain") or "").strip()

        if not title:
            self.add_error("title", "Title is required.")

        if starts_at and ends_at and ends_at <= starts_at:
            self.add_error("ends_at", "End time must be after start time.")

        # Reasonable limits (security + UX)
        if early is not None and early > 120:
            self.add_error("join_early_minutes", "Join early minutes must be 120 or less.")
        if late is not None and late > 240:
            self.add_error("join_late_minutes", "Join late minutes must be 240 or less.")

        # Mode rules
        needs_online = mode in ("online", "both")
        upload_only = mode == "upload"

        if needs_online:
            # If domain not provided, we still allow and fallback in join_meeting to meet.jit.si,
            # but it's better to be explicit in production.
            # If you want to force it: uncomment next 2 lines.
            # if not domain:
            #     self.add_error("jitsi_domain", "Jitsi domain is required for online meetings.")
            pass

        if upload_only:
            # No need to store domain if meeting has no online mode
            cleaned["jitsi_domain"] = ""

        return cleaned
