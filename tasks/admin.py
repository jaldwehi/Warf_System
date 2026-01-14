
from django.contrib import admin, messages
from django.core.exceptions import ValidationError

from .models import Task


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "assigned_to",
        "status",
        "priority",
        "due_date",
        "meeting",
        "minutes",
        "created_at",
    )
    list_filter = ("status", "priority", "meeting")
    search_fields = ("title", "assigned_to__username", "assigned_to__email")
    ordering = ("-created_at",)

    # (اختياري) يعطي تجربة أسهل في الأدمن بدل dropdown كبير
    autocomplete_fields = ("meeting", "minutes", "assigned_to")

    def _minutes_approved_or_none(self, obj: Task) -> bool:
        """
        True إذا:
        - ما فيه minutes مرتبطة (None)
        - أو status = approved
        """
        if not obj.minutes_id:
            return True
        return obj.minutes.status == "approved"

    def has_change_permission(self, request, obj=None):
        """
        يمنع تعديل مهمة مرتبطة بمحضر غير معتمد (إلا للسوبر يوزر).
        """
        if obj and not request.user.is_superuser and not self._minutes_approved_or_none(obj):
            return False
        return super().has_change_permission(request, obj)

    def has_delete_permission(self, request, obj=None):
        """
        يمنع حذف مهمة مرتبطة بمحضر غير معتمد (إلا للسوبر يوزر).
        """
        if obj and not request.user.is_superuser and not self._minutes_approved_or_none(obj):
            return False
        return super().has_delete_permission(request, obj)

    def save_model(self, request, obj, form, change):
        """
        يمنع حفظ/إنشاء Task إذا كانت مرتبطة بمحضر غير approved (إلا للسوبر يوزر).
        """
        if obj.minutes_id and not request.user.is_superuser:
            if obj.minutes.status != "approved":
                raise ValidationError("You can't create/update tasks until Minutes is approved.")

        super().save_model(request, obj, form, change)

        if obj.minutes_id and obj.minutes.status == "approved":
            messages.success(request, "Task saved successfully (Minutes is approved).")

