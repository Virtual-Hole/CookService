from rest_framework.views import APIView
from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from drf_spectacular.utils import OpenApiResponse, extend_schema

from foods.models import FoodCategory, Food, FoodMenuBranchCollection, FoodMenuBranch
from foods.serializers import (
    FoodCategorySerializer, FoodCategoryCreateSerializer,
    FoodSerializer, FoodCreateSerializer,
    FoodMenuBranchCollectionSerializer, FoodMenuBranchCollectionCreateSerializer,
    FoodMenuBranchSerializer, FoodMenuBranchCreateSerializer
)
from custom_user.pagination import CustomPageNumberPagination
from custom_user.serializers import ErrorResponseSerializer


# FoodCategory Views
class FoodCategoryListView(ListAPIView):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=FoodCategorySerializer(many=True),
                description='Food Category ro\'yxati'
            ),
        },
        tags=['Foods'],
        summary='Food Category ro\'yxati',
        description='Barcha food categorylar (pagination bilan)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FoodCategoryCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FoodCategoryCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=FoodCategorySerializer,
                description='Food Category muvaffaqiyatli yaratildi'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Validatsiya xatosi'
            ),
        },
        tags=['Foods'],
        summary='Yangi Food Category qo\'shish',
    )
    def post(self, request):
        serializer = FoodCategoryCreateSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            error_msg = errors[first_field][0]

            return Response(
                {'success': False, 'error': error_msg, 'errorStatus': 'data_credential'},
                status=status.HTTP_400_BAD_REQUEST
            )

        category = serializer.save()

        return Response({
            'success': True,
            'message': 'Food Category added successfully.',
            'data': FoodCategorySerializer(category, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class FoodCategoryDetailView(RetrieveAPIView):
    queryset = FoodCategory.objects.all()
    serializer_class = FoodCategorySerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @extend_schema(
        responses={
            200: FoodCategorySerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Foods'],
        summary='Food Category ma\'lumotlari',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# Food Views
class FoodListView(ListAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=FoodSerializer(many=True),
                description='Food ro\'yxati'
            ),
        },
        tags=['Foods'],
        summary='Food ro\'yxati',
        description='Barcha foodlar (pagination bilan)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FoodCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FoodCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=FoodSerializer,
                description='Food muvaffaqiyatli yaratildi'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Validatsiya xatosi'
            ),
        },
        tags=['Foods'],
        summary='Yangi Food qo\'shish',
    )
    def post(self, request):
        serializer = FoodCreateSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            error_msg = errors[first_field][0]

            return Response(
                {'success': False, 'error': error_msg, 'errorStatus': 'data_credential'},
                status=status.HTTP_400_BAD_REQUEST
            )

        food = serializer.save()

        return Response({
            'success': True,
            'message': 'Food added successfully.',
            'data': FoodSerializer(food, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class FoodDetailView(RetrieveAPIView):
    queryset = Food.objects.all()
    serializer_class = FoodSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @extend_schema(
        responses={
            200: FoodSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Foods'],
        summary='Food ma\'lumotlari',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


# FoodMenuBranchCollection Views
class FoodMenuBranchCollectionListView(ListAPIView):
    queryset = FoodMenuBranchCollection.objects.all()
    serializer_class = FoodMenuBranchCollectionSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=FoodMenuBranchCollectionSerializer(many=True),
                description='Food Menu Branch Collection ro\'yxati'
            ),
        },
        tags=['Foods'],
        summary='Food Menu Branch Collection ro\'yxati',
        description='Barcha food menu branch collectionlar (pagination bilan)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


class FoodMenuBranchCollectionCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FoodMenuBranchCollectionCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=FoodMenuBranchCollectionSerializer,
                description='Food Menu Branch Collection muvaffaqiyatli yaratildi'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Validatsiya xatosi'
            ),
        },
        tags=['Foods'],
        summary='Yangi Food Menu Branch Collection qo\'shish',
    )
    def post(self, request):
        serializer = FoodMenuBranchCollectionCreateSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            error_msg = errors[first_field][0]

            return Response(
                {'success': False, 'error': error_msg, 'errorStatus': 'data_credential'},
                status=status.HTTP_400_BAD_REQUEST
            )

        collection = serializer.save()

        return Response({
            'success': True,
            'message': 'Food Menu Branch Collection added successfully.',
            'data': FoodMenuBranchCollectionSerializer(collection, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class FoodMenuBranchCollectionDetailView(RetrieveAPIView):
    queryset = FoodMenuBranchCollection.objects.all()
    serializer_class = FoodMenuBranchCollectionSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @extend_schema(
        responses={
            200: FoodMenuBranchCollectionSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Foods'],
        summary='Food Menu Branch Collection ma\'lumotlari',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)


# FoodMenuBranch Views
class FoodMenuBranchListView(ListAPIView):
    queryset = FoodMenuBranch.objects.all()
    serializer_class = FoodMenuBranchSerializer
    pagination_class = CustomPageNumberPagination
    permission_classes = [IsAuthenticated]

    @extend_schema(
        responses={
            200: OpenApiResponse(
                response=FoodMenuBranchSerializer(many=True),
                description='Food Menu Branch ro\'yxati'
            ),
        },
        tags=['Foods'],
        summary='Food Menu Branch ro\'yxati',
        description='Barcha food menu branchlar (pagination bilan)',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context


class FoodMenuBranchCreateView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        request=FoodMenuBranchCreateSerializer,
        responses={
            201: OpenApiResponse(
                response=FoodMenuBranchSerializer,
                description='Food Menu Branch muvaffaqiyatli yaratildi'
            ),
            400: OpenApiResponse(
                response=ErrorResponseSerializer,
                description='Validatsiya xatosi'
            ),
        },
        tags=['Foods'],
        summary='Yangi Food Menu Branch qo\'shish',
    )
    def post(self, request):
        serializer = FoodMenuBranchCreateSerializer(data=request.data)

        if not serializer.is_valid():
            errors = serializer.errors
            first_field = next(iter(errors))
            error_msg = errors[first_field][0]

            return Response(
                {'success': False, 'error': error_msg, 'errorStatus': 'data_credential'},
                status=status.HTTP_400_BAD_REQUEST
            )

        menu_branch = serializer.save()

        return Response({
            'success': True,
            'message': 'Food Menu Branch added successfully.',
            'data': FoodMenuBranchSerializer(menu_branch, context={'request': request}).data
        }, status=status.HTTP_201_CREATED)


class FoodMenuBranchDetailView(RetrieveAPIView):
    queryset = FoodMenuBranch.objects.all()
    serializer_class = FoodMenuBranchSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'id'

    @extend_schema(
        responses={
            200: FoodMenuBranchSerializer,
            404: ErrorResponseSerializer,
        },
        tags=['Foods'],
        summary='Food Menu Branch ma\'lumotlari',
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context

