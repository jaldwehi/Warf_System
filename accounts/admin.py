from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DjangoUserAdmin

from .models import User, Profile


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    extra = 0
    fields = ("status", "face_image", "created_at")
    readonly_fields = ("created_at",)


@admin.register(User)
class UserAdmin(DjangoUserAdmin):
    """
    Admin configuration for custom User model.
    Shows Profile inline for quick management.
    """
    inlines = (ProfileInline,)

    list_display = ("username", "email", "first_name", "last_name", "is_active", "is_staff", "is_superuser")
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("username",)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    """
    Dedicated admin page for Profiles (Employees).
    Includes status management + face image indicator.
    """
    list_display = ("user", "status", "face_image_status", "created_at")
    list_filter = ("status",)
    search_fields = ("user__username", "user__email", "user__first_name", "user__last_name")
    ordering = ("user__username",)
    readonly_fields = ("created_at",)

    actions = ("mark_active", "mark_suspended", "mark_left")

    @admin.display(description="Face Image", boolean=True)
    def face_image_status(self, obj):
        return bool(obj.face_image)

    @admin.action(description="Set selected profiles to Active")
    def mark_active(self, request, queryset):
        queryset.update(status="active")

    @admin.action(description="Set selected profiles to Suspended")
    def mark_suspended(self, request, queryset):
        queryset.update(status="suspended")

    @admin.action(description="Set selected profiles to Left")
    def mark_left(self, request, queryset):
        queryset.update(status="left")
