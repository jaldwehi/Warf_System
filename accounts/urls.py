from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    # Employees management (Admin-only)
    path("employees/", views.employee_list, name="employee_list"),
    path(
        "employees/<int:pk>/toggle-status/",
        views.employee_toggle_status,
        name="employee_toggle_status",
    ),
    
    # Profile (Employee/Admin self profile)
    path("profile/", views.profile_view, name="profile"),

    # Face verification (used in meetings flow)
    path("face-verify/", views.face_verify, name="face_verify"),

    # Auth
    path("logout/", views.logout_view, name="logout"),

    path("employees/create/", views.employee_create, name="employee_create"),
    path("employees/<int:pk>/edit/", views.employee_edit, name="employee_edit"),

]
