from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class SendActivationCodeSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(required=True,
        help_text="Foydalanuvchi telefon raqami")

class SendActivationCodeResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    phone_number = serializers.IntegerField()

class VerifyActivationCodeSerializer(serializers.Serializer):
    phone_number = serializers.IntegerField(required=True,
        help_text="Foydalanuvchi telefon raqami")
    code = serializers.CharField(
        max_length=6,
        min_length=6,
        required=True,
        help_text="6 raqamli aktivatsiya kodi"
    )
    device_hardware = serializers.CharField(allow_null=True)

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Kod faqat raqamlardan iborat bo'lishi kerak")
        return value


class VerifyActivationCodeResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    access = serializers.CharField(help_text="JWT Access Token")
    refresh = serializers.CharField(help_text="JWT Refresh Token")

