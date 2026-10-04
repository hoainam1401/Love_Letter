from rest_framework import serializers
from .models import Player


class PlayerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Player
        fields = [
            "id",
            "username",
            "password",
            "total_matches",
            "total_win",
            "total_elim",
            "total_deaths",
            "total_tokens",
        ]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        player = Player.objects.create_user(**validated_data)
        return player
