from django.contrib import admin
from django.urls import path, include
from accounts import views as accounts_views
from core.views import role_redirect
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path("admin/", admin.site.urls),

    # Public pages
    path("", accounts_views.home, name="home"),
    path("login/", accounts_views.login_view, name="login"),
    path("logout/", accounts_views.logout_view, name="logout"),

    # Dashboards
    path("admin-panel/", accounts_views.admin_dashboard, name="admin_dashboard"),
    path("employee/", accounts_views.employee_dashboard, name="employee_dashboard"),
    path("redirect/", role_redirect, name="role_redirect"),

    # Apps
    path("accounts/", include("accounts.urls")),
    path("meetings/", include("meetings.urls")),
    path("minutes/", include("minutes.urls")),
    path("tasks/", include("tasks.urls")),
    path("assistant/", include("assistant.urls")),
    path("archive/", include("archive.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



