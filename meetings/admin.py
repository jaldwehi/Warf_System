from django.contrib import admin
from .models import Meeting, Attendee
from minutes.models import Minutes
from records.models import Record


class AttendeeInline(admin.TabularInline):
    model = Attendee
    extra = 1

# StackedInline لأن المحضر نصوص طويلة فشكله أفضل من جدول.v
class MinutesInline(admin.StackedInline):
    model = Minutes
    extra = 0
    max_num = 1 #max_num=1 لأن الاجتماع له محضر واحد.
    
    exclude = ("created_by", "approved_by", "approved_at")


    #أي Minutes تنضاف من داخل Meeting
     #تتسجّل تلقائيًا باسم المستخدم الحالي (الأدمن/الموظف)
    def save_new_instance(self, request, obj, form, change):
        obj.created_by = request.user
        return super().save_new_instance(request, obj, form, change)



    
@admin.register(Meeting)
class MeetingAdmin(admin.ModelAdmin):
    list_display = ("title", "scheduled_at", "organizer")
    search_fields = ("title", "organizer__username")
    list_filter = ("scheduled_at",)
    inlines = [MinutesInline, AttendeeInline]
    def save_formset(self, request, form, formset, change):
        instances = formset.save(commit=False)
        for obj in instances:
            # لو هذا Minutes وانضاف من داخل Meeting
            if isinstance(obj, Minutes) and not getattr(obj, "created_by_id", None):
                obj.created_by = request.user
            obj.save()
        formset.save_m2m()

