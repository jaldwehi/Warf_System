from django.urls import path
from . import views

app_name = "assistant"

urlpatterns = [
    path("", views.chat_view, name="chat"),
    path("ask/", views.ask_api, name="ask"),
]
