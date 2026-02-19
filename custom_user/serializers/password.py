from rest_framework import serializers


class ForgotPasswordSerializer(serializers.Serializer):
    phone_number = serializers.CharField(required=True, max_length=15, help_text="User phone number")

    def validate_phone_number(self, value):
        if not value:
            raise serializers.ValidationError("Phone number is required")
        return value


class ForgotPasswordResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
    phone_number = serializers.CharField()

class ForgotPasswordCompleteSerializer(serializers.Serializer):
    reset_token = serializers.UUIDField(required=True, help_text="Reset token (UUID)")
    new_password = serializers.CharField(min_length=8, required=True, write_only=True, help_text="Yangi parol")


class ForgotPasswordCompleteResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()


class VerifyCodeUniversalResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()

    access = serializers.CharField(required=False, help_text="JWT Access Token (faqat register)")
    refresh = serializers.CharField(required=False, help_text="JWT Refresh Token (faqat register)")

    reset_token = serializers.UUIDField(required=False, help_text="Reset token UUID (faqat forgot)")

class ResetPasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(min_length=8, required=True, write_only=True, help_text='Old parol')
    new_password = serializers.CharField(min_length=8, required=True, write_only=True, help_text="New parol")


class ResetPasswordResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()
