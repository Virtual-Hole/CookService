from rest_framework import serializers
from django.contrib.auth import get_user_model
from custom_user.phone import normalize_uz_phone

User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    phone_number = serializers.CharField(max_length=15, required=True)
    full_name = serializers.CharField(max_length=30, required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = User
        fields = ('email', 'phone_number', 'full_name', 'password')

    def validate_phone_number(self, value):
        try:
            normalized = normalize_uz_phone(value)
        except ValueError as exc:
            raise serializers.ValidationError(str(exc))

        if User.objects.filter(phone_number=normalized).exists():
            raise serializers.ValidationError("Bu raqam allaqachon ro'yxatdan o'tgan")
        return normalized

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data.get('email'),
            password=validated_data['password'],
            phone_number=validated_data['phone_number'],
            full_name=validated_data.get('full_name', ''),
            role=User.RoleChoices.USER,
            is_active=False
        )
        return user


class UserRegistrationResponseSerializer(serializers.Serializer):
    success = serializers.BooleanField()
    message = serializers.CharField()

