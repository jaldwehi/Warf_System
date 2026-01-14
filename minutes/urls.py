from django.urls import path
from . import views

app_name = "minutes"

urlpatterns = [
    path("", views.minutes_home, name="home"),
    path("all/", views.minutes_list, name="list"),
    path("meeting/<int:meeting_id>/", views.minutes_for_meeting, name="meeting_minutes"),
]

