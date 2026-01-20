from rest_framework.generics import ListAPIView, RetrieveAPIView
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import OpenApiResponse, extend_schema

from foods.models import FoodCategory, Food, FoodMenuBranchCollection, FoodMenuBranch
from foods.serializers import (
    FoodCategorySerializer,
    FoodSerializer,
    FoodMenuBranchCollectionSerializer,
    FoodMenuBranchSerializer,
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
