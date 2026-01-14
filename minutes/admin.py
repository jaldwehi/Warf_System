from django.contrib import admin
from .models import Minutes
from tasks.models import Task
from records.models import Record

class TaskInline(admin.TabularInline):
    model = Task
    extra = 1
    fields = ("title", "assignee", "status", "priority", "due_date")
    
    def has_add_permission(self, request, obj=None):
        # obj هنا هو Minutes
        if obj and obj.status != "approved":
            return False
        return True


@admin.register(Minutes)
class MinutesAdmin(admin.ModelAdmin):
    search_fields = ("meeting__title", "summary", "discussion_points")
    list_display = ("meeting", "status", "created_by", "approved_by")
    readonly_fields = ("created_by", "approved_by", "approved_at")
    inlines = [TaskInline]

    actions = ["approve_minutes"]

    def approve_minutes(self, request, queryset):
        for minutes in queryset.filter(status__in=["draft", "review"]):
            minutes.approve(request.user)

    approve_minutes.short_description = "Approve selected minutes"

    def has_add_permission(self, request):
        return False

# لا يمكن إضافة Minutes من هنا
#فقط من داخل Meeting (Inline)

    def save_formset(self, request, form, formset, change):
     instances = formset.save(commit=False)
     for obj in instances:
        if isinstance(obj, Record) and not obj.created_by_id:
            obj.created_by = request.user
        obj.save()
     formset.save_m2m()
