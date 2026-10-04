from django.shortcuts import render
from django.contrib.auth.models import User
from .models import Player
from rest_framework import generics
from .serializers import PlayerSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny


# Create your views here.
class CreatePlayerView(generics.CreateAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]


class ListPlayerView(generics.ListAPIView):
    queryset = Player.objects.all()
    serializer_class = PlayerSerializer
    permission_classes = [AllowAny]
