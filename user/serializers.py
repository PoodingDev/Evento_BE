from rest_framework import serializers

from .models import User


class UserSerializer(serializers.ModelSerializer):
    birth = serializers.DateField(
        format="%Y-%m-%d",
        input_formats=["%Y-%m-%d"],
        error_messages={
            "invalid": "날짜 형식이 올바르지 않음. YYYY-MM-DD 형식을 사용하세요."
        },
    )

    class Meta:
        model = User
        fields = ["email", "username", "birth", "password"]
        extra_kwargs = {
            "password": {"write_only": True},
            "email": {"required": True},
            "username": {"required": True},
            "birth": {"required": True},
        }

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["nickname", "birth", "is_birth_public"]
