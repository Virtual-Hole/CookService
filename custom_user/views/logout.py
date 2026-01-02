from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from drf_spectacular.utils import extend_schema

from custom_user.serializers import LogoutSerializer

class LogoutView(generics.GenericAPIView):
    permission_classes = (IsAuthenticated, )
    serializer_class = LogoutSerializer

    @extend_schema(
        tags=['Authentication']
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            refresh_token = serializer.validated_data['refresh_token']
            token = RefreshToken(refresh_token)
            token.blacklist()

            response_data = {
                'success': True,
                'message': 'Successfully logged out.'
            }

            return Response(data=response_data, status=status.HTTP_200_OK)

        except:
            return Response(
                {
                    'success': False,
                    'errorStatus': 'data_credential',
                    'error': 'Invalid token or already blacklisted.'
                },
                status=status.HTTP_400_BAD_REQUEST
            )