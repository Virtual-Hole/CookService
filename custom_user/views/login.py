from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema, OpenApiResponse
from django.utils import timezone

from custom_user.models import Device
from custom_user.serializers import (
    BranchAdminLoginResponseSerializer,
    BranchAdminLoginSerializer,
    ErrorResponseSerializer,
    RestaurantAdminLoginResponseSerializer,
    RestaurantAdminLoginSerializer,
    SuperAdminLoginResponseSerializer,
    SuperAdminLoginSerializer,
    UserLoginSerializer,
    UserLoginResponseSerializer,
)
from custom_user.services import get_device_info, get_location_by_ip, get_client_ip
from custom_user.utils import get_tokens_for_user

User = get_user_model()


def _login_error_response(error_message, status_code=status.HTTP_400_BAD_REQUEST, error_status='data_credential'):
    return Response(
        {'success': False, 'error': error_message, 'errorStatus': error_status},
        status=status_code
    )


def _save_device_session(request, user, device_hardware, tokens):
    if not device_hardware:
        return

    ip_address = get_client_ip(request)
    location_city = get_location_by_ip(ip_address)
    device_info = get_device_info(request)
    device_model = device_info.get('device_model', '')

    device, _ = Device.objects.update_or_create(
        user=user,
        device_hardware=device_hardware,
        defaults={
            'device_ip': ip_address,
            'device_name': device_model,
            'location_city': location_city if location_city else '',
            'access_token': tokens['access'],
            'refresh_token': tokens['refresh'],
        }
    )

    device.last_online = timezone.now()
    device.save(update_fields=['last_online'])


def _role_based_login(request, serializer_class, expected_role, forbidden_message, success_message):
    serializer = serializer_class(data=request.data)

    if not serializer.is_valid():
        errors = serializer.errors
        first_field = next(iter(errors))
        error_msg = errors[first_field][0]
        return _login_error_response(error_msg)

    phone_number = serializer.validated_data['phone_number']
    password = serializer.validated_data['password']

    try:
        user = User.objects.get(phone_number=phone_number)
    except User.DoesNotExist:
        return _login_error_response('Incorrect phone number or password.')

    if not user.check_password(password):
        return _login_error_response('Incorrect phone number or password.')

    if user.role != expected_role:
        return _login_error_response(
            forbidden_message,
            status_code=status.HTTP_403_FORBIDDEN,
            error_status='forbidden',
        )

    if not user.is_active:
        return _login_error_response(
            'Account not activated.',
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_status='not_activated',
        )

    tokens = get_tokens_for_user(user)
    return Response(
        {
            'success': True,
            'message': success_message,
            'login_response': {
                'access': tokens['access'],
                'refresh': tokens['refresh'],
            }
        },
        status=status.HTTP_200_OK
    )


class UserLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=UserLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=UserLoginResponseSerializer,
                description='Login muvaffaqiyatli, JWT tokenlar berildi'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Raqam yoki parol noto\'g\'ri'
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Akkount aktivlashtirilmagan'
            ),
        },
        tags=['Authentication'],
        summary='Login qilish',
        description='Telefon raqam va parol bilan login qilib JWT tokenlarni olish'
    )
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            error_msg = errors[first_field][0]
            return _login_error_response(error_msg)

        phone_number = serializer.validated_data['phone_number']
        password = serializer.validated_data['password']
        device_hardware = serializer.validated_data.get('device_hardware') or None

        try:
            user = User.objects.get(phone_number=phone_number)

            if not user.check_password(password):
                return _login_error_response('Incorrect phone number or password.')

            if user.role == User.RoleChoices.SUPER_ADMIN:
                return _login_error_response(
                    'Super admin must use super-admin login endpoint.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    error_status='forbidden',
                )
            if user.role == User.RoleChoices.RESTAURANT_ADMIN:
                return _login_error_response(
                    'Restaurant admin must use restaurant-admin login endpoint.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    error_status='forbidden',
                )
            if user.role == User.RoleChoices.BRANCH_ADMIN:
                return _login_error_response(
                    'Branch admin must use branch-admin login endpoint.',
                    status_code=status.HTTP_403_FORBIDDEN,
                    error_status='forbidden',
                )

            if not user.is_active:
                return _login_error_response(
                    'Account not activated. Please enter the code sent to your phone number.',
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    error_status='not_activated',
                )

            tokens = get_tokens_for_user(user, device_hardware=device_hardware)
            _save_device_session(request, user, device_hardware, tokens)

            response_data = {
                'success': True,
                'message': 'Login muvaffaqiyatli',
                'login_response': {
                    'access': tokens['access'],
                    'refresh': tokens['refresh'],
                }
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return _login_error_response('Incorrect phone number or password.')


class SuperAdminLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=SuperAdminLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=SuperAdminLoginResponseSerializer,
                description='Super admin login muvaffaqiyatli'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Raqam yoki parol noto\'g\'ri'
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Akkount aktivlashtirilmagan'
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Foydalanuvchi super admin emas'
            ),
        },
        tags=['Authentication'],
        summary='Super admin login',
        description='Faqat super admin uchun login endpoint'
    )
    def post(self, request):
        return _role_based_login(
            request=request,
            serializer_class=SuperAdminLoginSerializer,
            expected_role=User.RoleChoices.SUPER_ADMIN,
            forbidden_message='Only super admin can use this endpoint.',
            success_message='Super admin login successful',
        )


class RestaurantAdminLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=RestaurantAdminLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=RestaurantAdminLoginResponseSerializer,
                description='Restaurant admin login muvaffaqiyatli'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Raqam yoki parol noto\'g\'ri'
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Akkount aktivlashtirilmagan'
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Foydalanuvchi restaurant admin emas'
            ),
        },
        tags=['Authentication'],
        summary='Restaurant admin login',
        description='Faqat restaurant admin uchun login endpoint'
    )
    def post(self, request):
        return _role_based_login(
            request=request,
            serializer_class=RestaurantAdminLoginSerializer,
            expected_role=User.RoleChoices.RESTAURANT_ADMIN,
            forbidden_message='Only restaurant admin can use this endpoint.',
            success_message='Restaurant admin login successful',
        )


class BranchAdminLoginView(APIView):
    permission_classes = [AllowAny]

    @extend_schema(
        request=BranchAdminLoginSerializer,
        responses={
            200: OpenApiResponse(
                response=BranchAdminLoginResponseSerializer,
                description='Branch admin login muvaffaqiyatli'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Raqam yoki parol noto\'g\'ri'
            ),
            401: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Akkount aktivlashtirilmagan'
            ),
            403: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Foydalanuvchi branch admin emas'
            ),
        },
        tags=['Authentication'],
        summary='Branch admin login',
        description='Faqat branch admin uchun login endpoint'
    )
    def post(self, request):
        return _role_based_login(
            request=request,
            serializer_class=BranchAdminLoginSerializer,
            expected_role=User.RoleChoices.BRANCH_ADMIN,
            forbidden_message='Only branch admin can use this endpoint.',
            success_message='Branch admin login successful',
        )
