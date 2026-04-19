from rest_framework import serializers
from djoser.serializers import UserSerializer
from django.contrib.auth import get_user_model
from custom_user.phone import normalize_uz_phone

User = get_user_model()

class CustomUserSerializer(UserSerializer):
    class Meta(UserSerializer.Meta):
        model = User
        fields = ("id", "uid", "courier_id", "email", "phone_number", "full_name", "profile_photo", 'notification', 'promotional_notification')
        read_only_fields = ("id", "uid", "courier_id")


class NotificationSettingsSerializer(serializers.Serializer):
    notification = serializers.BooleanField(required=False, help_text="Oddiy bildirishnomalar")
    promotional_notification = serializers.BooleanField(required=False, help_text="Reklama bildirishnomalari")

    def validate(self, data):
        if not data:
            raise serializers.ValidationError("Kamida bitta sozlama yuborilishi kerak")
        return data


class NotificationSettingsResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class ProfilePhotoSerializer(serializers.Serializer):
    profile_photo = serializers.ImageField()


class ErrorResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    error = serializers.CharField()
    errorStatus = serializers.CharField()


class VerifyCodeUniversalSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=15, help_text="User phone number")
    code = serializers.CharField(max_length=6, min_length=6, required=True, help_text="6 raqamli kod")
    request_type = serializers.ChoiceField(
        choices=['register', 'forgot'],
        required=True,
        help_text="'register' yoki 'forgot'"
    )
    device_hardware = serializers.CharField(
        max_length=100,
        required=False,
        allow_blank=True,
        help_text="Qurilma nomi (faqat register uchun)"
    )

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError("Kod faqat raqamlardan iborat bo'lishi kerak")
        return value

    def validate_phone_number(self, value):
        try:
            return normalize_uz_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

    def validate(self, data):
        if data['request_type'] == 'register':
            if not data.get('device_hardware'):
                pass
        return data


class VerifyCodeUniversalResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()

    # Faqat register uchun
    access = serializers.CharField(required=False, help_text="JWT Access Token (faqat register)")
    refresh = serializers.CharField(required=False, help_text="JWT Refresh Token (faqat register)")


class LogoutSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(help_text='refresh_token for blacklisting')
