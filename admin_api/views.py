from django.contrib.auth import get_user_model
from django.db.models import Q
from rest_framework import generics, status, viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, extend_schema_view

from custom_user.pagination import CustomPageNumberPagination
from custom_user.permissions import IsBranchAdmin, IsRestaurantAdmin, IsSuperAdmin
from foods.models import Food, FoodCategory, FoodMenuBranch, FoodMenuBranchCollection
from restaurants.models import Restaurants, RestaurantBranches

from admin_api.serializers import (
    AdminFoodCategorySerializer,
    AdminFoodMenuBranchCollectionSerializer,
    AdminFoodMenuBranchSerializer,
    AdminFoodSerializer,
    BranchAdminSelfSerializer,
    SuperAdminRestaurantAdminUserSerializer,
    SuperAdminRestaurantSerializer,
    RestaurantAdminBranchAdminUserSerializer,
    RestaurantAdminBranchSerializer,
    RestaurantAdminRestaurantSerializer,
)


User = get_user_model()


def _tag_viewset(tag):
    return extend_schema_view(
        list=extend_schema(tags=[tag]),
        retrieve=extend_schema(tags=[tag]),
        create=extend_schema(tags=[tag]),
        update=extend_schema(tags=[tag]),
        partial_update=extend_schema(tags=[tag]),
        destroy=extend_schema(tags=[tag]),
    )


def _tag_readonly_viewset(tag):
    return extend_schema_view(
        list=extend_schema(tags=[tag]),
        retrieve=extend_schema(tags=[tag]),
    )


class RestaurantAdminBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsRestaurantAdmin]
    pagination_class = CustomPageNumberPagination

    def get_allowed_restaurants(self):
        return self.request.user.managed_restaurants.all()

    def get_allowed_branches(self):
        return RestaurantBranches.objects.filter(restaurant__in=self.get_allowed_restaurants())

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["allowed_branches"] = self.get_allowed_branches()
        return context


class RestaurantAdminReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsRestaurantAdmin]
    pagination_class = CustomPageNumberPagination


class BranchAdminBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    pagination_class = CustomPageNumberPagination

    def get_allowed_branches(self):
        return self.request.user.managed_branches.all()

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context["allowed_branches"] = self.get_allowed_branches()
        return context


class BranchAdminReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    pagination_class = CustomPageNumberPagination


class SuperAdminBaseViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = CustomPageNumberPagination


@_tag_viewset("Super Admin - Restaurants")
class SuperAdminRestaurantViewSet(SuperAdminBaseViewSet):
    serializer_class = SuperAdminRestaurantSerializer
    queryset = Restaurants.objects.all()


@_tag_viewset("Super Admin - Branches")
class SuperAdminBranchViewSet(SuperAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchSerializer
    queryset = RestaurantBranches.objects.all()


@_tag_viewset("Super Admin - Restaurant Admins")
class SuperAdminRestaurantAdminUserViewSet(SuperAdminBaseViewSet):
    serializer_class = SuperAdminRestaurantAdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(role="restaurant_admin")


@_tag_viewset("Super Admin - Branch Admins")
class SuperAdminBranchAdminUserViewSet(SuperAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchAdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(role="branch_admin")


@_tag_viewset("Restaurant Admin - Branch Admins")
class RestaurantAdminBranchAdminUserViewSet(RestaurantAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchAdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role != "restaurant_admin":
            return User.objects.none()

        allowed_branches = self.get_allowed_branches()
        return User.objects.filter(
            Q(role="branch_admin", managed_branches__in=allowed_branches) | Q(pk=user.pk)
        ).distinct()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.pk == request.user.pk:
            return Response(
                {"detail": "You cannot delete yourself."},
                status=status.HTTP_403_FORBIDDEN,
            )
        return super().destroy(request, *args, **kwargs)


@_tag_readonly_viewset("Restaurant Admin - Restaurants")
class RestaurantAdminRestaurantViewSet(RestaurantAdminReadOnlyViewSet):
    serializer_class = RestaurantAdminRestaurantSerializer
    queryset = Restaurants.objects.all()

    def get_queryset(self):
        return self.request.user.managed_restaurants.all()


@_tag_viewset("Restaurant Admin - Branches")
class RestaurantAdminBranchViewSet(RestaurantAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchSerializer
    queryset = RestaurantBranches.objects.all()

    def get_queryset(self):
        return self.get_allowed_branches()

    def perform_create(self, serializer):
        allowed_restaurants = self.get_allowed_restaurants()
        restaurant = serializer.validated_data.get("restaurant")

        if restaurant is None:
            if allowed_restaurants.count() == 1:
                restaurant = allowed_restaurants.first()
            else:
                raise ValidationError({"restaurant": "Restaurant is required."})

        if not allowed_restaurants.filter(pk=restaurant.pk).exists():
            raise ValidationError({"restaurant": "Restaurant is not allowed."})

        serializer.save(restaurant=restaurant)

    def perform_update(self, serializer):
        if "restaurant" in serializer.validated_data:
            if serializer.validated_data["restaurant"] != serializer.instance.restaurant:
                raise ValidationError({"restaurant": "You cannot change restaurant."})
        serializer.save()


@_tag_viewset("Restaurant Admin - Food Categories")
class RestaurantAdminFoodCategoryViewSet(RestaurantAdminBaseViewSet):
    serializer_class = AdminFoodCategorySerializer
    queryset = FoodCategory.objects.all()

    def get_queryset(self):
        return FoodCategory.objects.filter(branch__in=self.get_allowed_branches())


@_tag_viewset("Restaurant Admin - Foods")
class RestaurantAdminFoodViewSet(RestaurantAdminBaseViewSet):
    serializer_class = AdminFoodSerializer
    queryset = Food.objects.all()

    def get_queryset(self):
        return Food.objects.filter(category__branch__in=self.get_allowed_branches())


@_tag_viewset("Restaurant Admin - Menu Collections")
class RestaurantAdminMenuCollectionViewSet(RestaurantAdminBaseViewSet):
    serializer_class = AdminFoodMenuBranchCollectionSerializer
    queryset = FoodMenuBranchCollection.objects.all()

    def get_queryset(self):
        return FoodMenuBranchCollection.objects.filter(branch__in=self.get_allowed_branches())


@_tag_viewset("Restaurant Admin - Menu Branches")
class RestaurantAdminMenuBranchViewSet(RestaurantAdminBaseViewSet):
    serializer_class = AdminFoodMenuBranchSerializer
    queryset = FoodMenuBranch.objects.all()

    def get_queryset(self):
        return FoodMenuBranch.objects.filter(collection__branch__in=self.get_allowed_branches())


@extend_schema(tags=["Branch Admin - Profile"])
class BranchAdminProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated, IsBranchAdmin]
    serializer_class = BranchAdminSelfSerializer
    http_method_names = ["get", "patch", "put"]

    def get_object(self):
        return self.request.user


@_tag_readonly_viewset("Branch Admin - Branches")
class BranchAdminBranchViewSet(BranchAdminReadOnlyViewSet):
    serializer_class = RestaurantAdminBranchSerializer
    queryset = RestaurantBranches.objects.all()

    def get_queryset(self):
        return self.request.user.managed_branches.all()


@_tag_viewset("Branch Admin - Food Categories")
class BranchAdminFoodCategoryViewSet(BranchAdminBaseViewSet):
    serializer_class = AdminFoodCategorySerializer
    queryset = FoodCategory.objects.all()

    def get_queryset(self):
        return FoodCategory.objects.filter(branch__in=self.get_allowed_branches())


@_tag_viewset("Branch Admin - Foods")
class BranchAdminFoodViewSet(BranchAdminBaseViewSet):
    serializer_class = AdminFoodSerializer
    queryset = Food.objects.all()

    def get_queryset(self):
        return Food.objects.filter(category__branch__in=self.get_allowed_branches())


@_tag_viewset("Branch Admin - Menu Collections")
class BranchAdminMenuCollectionViewSet(BranchAdminBaseViewSet):
    serializer_class = AdminFoodMenuBranchCollectionSerializer
    queryset = FoodMenuBranchCollection.objects.all()

    def get_queryset(self):
        return FoodMenuBranchCollection.objects.filter(branch__in=self.get_allowed_branches())


@_tag_viewset("Branch Admin - Menu Branches")
class BranchAdminMenuBranchViewSet(BranchAdminBaseViewSet):
    serializer_class = AdminFoodMenuBranchSerializer
    queryset = FoodMenuBranch.objects.all()

    def get_queryset(self):
        return FoodMenuBranch.objects.filter(collection__branch__in=self.get_allowed_branches())
