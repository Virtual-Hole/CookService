from rest_framework import serializers
from django.contrib.auth import get_user_model
from custom_user.phone import normalize_uz_phone

User = get_user_model()

class UserLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=15)
    password = serializers.CharField(required=True, write_only=True, min_length=8)
    device_hardware = serializers.CharField(required=False, allow_blank=True)

    def validate_phone_number(self, value):
        try:
            return normalize_uz_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))


class TokenPairSerializer(serializers.Serializer):
    access = serializers.CharField(help_text="JWT Access Token")
    refresh = serializers.CharField(help_text="JWT Refresh Token")


class UserLoginResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    login_response = TokenPairSerializer()


class SuperAdminLoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=15)
    password = serializers.CharField(required=True, write_only=True, min_length=8)

    def validate_phone_number(self, value):
        try:
            return normalize_uz_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))


class SuperAdminLoginResponseSerializer(UserLoginResponseSerializer):
    pass
