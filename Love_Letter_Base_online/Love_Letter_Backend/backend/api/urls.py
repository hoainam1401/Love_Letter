from django.urls import path
from . import views

urlpatterns = [
    path("player/list", views.ListPlayerView.as_view()),
]
