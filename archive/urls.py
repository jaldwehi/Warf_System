from django.urls import path
from . import views

app_name = "archive"

urlpatterns = [
    path("", views.archive_home, name="home"),
    path("solutions/", views.archive_solutions, name="solutions"),
    path("minutes/", views.archive_minutes, name="minutes"),
    path("attachments/", views.archive_attachments, name="attachments"),
]
