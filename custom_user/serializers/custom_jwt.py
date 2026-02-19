from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from custom_user.models import Device


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        device = Device.objects.filter(user=self.user).first()

        refresh = self.get_token(self.user)

        if device and device.device_hardware:
            refresh['device_hardware'] = device.device_hardware

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)

        if device:
            device.access_token = data['access']
            device.refresh_token = data['refresh']
            device.save(update_fields=['access_token', 'refresh_token'])

        return data

    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)
        return token


class CustomTokenRefreshSerializer(TokenRefreshSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)

        refresh_token_str = attrs['refresh']

        try:
            refresh_token = RefreshToken(refresh_token_str)
            device_hardware = refresh_token.get('device_hardware')
            user_id = refresh_token.get('user_id')

            if device_hardware and user_id:
                Device.objects.filter(
                    user_id=user_id,
                    device_hardware=device_hardware
                ).update(
                    access_token=data['access'],
                )
        except Exception:
            raise serializers.ValidationError({'error': 'Invalid refresh token'})

        return data
