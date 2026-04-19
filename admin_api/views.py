from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from drf_spectacular.utils import extend_schema, extend_schema_view
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from admin_api.serializers import (
    AdminFoodCategorySerializer,
    AdminFoodMenuBranchCollectionSerializer,
    AdminFoodMenuBranchSerializer,
    AdminFoodSerializer,
    BranchAdminSelfSerializer,
    OrderSerializer,
    RestaurantAdminBranchAdminUserSerializer,
    RestaurantAdminBranchSerializer,
    RestaurantAdminRestaurantSerializer,
    SuperAdminCourierSerializer,
    SuperAdminFoodCategorySerializer,
    SuperAdminRestaurantAdminUserSerializer,
    SuperAdminRestaurantSerializer,
    VehicleTypeSerializer,
)
from custom_user.models import VehicleType
from custom_user.pagination import CustomPageNumberPagination
from custom_user.permissions import IsBranchAdmin, IsRestaurantAdmin, IsSuperAdmin
from foods.models import Food, FoodCategory, FoodMenuBranch, FoodMenuBranchCollection
from restaurants.models import Order, Restaurants, RestaurantBranches


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


class SuperAdminReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated, IsSuperAdmin]
    pagination_class = CustomPageNumberPagination


@_tag_viewset("Super Admin - Restaurants")
class SuperAdminRestaurantViewSet(SuperAdminBaseViewSet):
    serializer_class = SuperAdminRestaurantSerializer
    queryset = Restaurants.objects.all()

    def get_queryset(self):
        return Restaurants.objects.all().prefetch_related("admins")

    @extend_schema(tags=["Super Admin - Restaurants"])
    @action(detail=False, methods=["get"], url_path="without-admins")
    def without_admins(self, request):
        queryset = self.filter_queryset(
            self.get_queryset()
            .annotate(
                restaurant_admin_count=Count(
                    "admins",
                    filter=Q(admins__role=User.RoleChoices.RESTAURANT_ADMIN),
                )
            )
            .filter(restaurant_admin_count=0)
        )

        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


@_tag_viewset("Super Admin - Branches")
class SuperAdminBranchViewSet(SuperAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchSerializer
    queryset = RestaurantBranches.objects.all()


@_tag_viewset("Super Admin - Restaurant Admins")
class SuperAdminRestaurantAdminUserViewSet(SuperAdminBaseViewSet):
    serializer_class = SuperAdminRestaurantAdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(role=User.RoleChoices.RESTAURANT_ADMIN)


@_tag_viewset("Super Admin - Branch Admins")
class SuperAdminBranchAdminUserViewSet(SuperAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchAdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(role=User.RoleChoices.BRANCH_ADMIN)


@_tag_viewset("Super Admin - Couriers")
class SuperAdminCourierViewSet(SuperAdminBaseViewSet):
    serializer_class = SuperAdminCourierSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        return User.objects.filter(role=User.RoleChoices.COURIER)


@_tag_viewset("Super Admin - Vehicle Types")
class SuperAdminVehicleTypeViewSet(SuperAdminBaseViewSet):
    serializer_class = VehicleTypeSerializer
    queryset = VehicleType.objects.select_related("user").all()


@_tag_viewset("Super Admin - Food Categories")
class SuperAdminFoodCategoryViewSet(SuperAdminBaseViewSet):
    serializer_class = SuperAdminFoodCategorySerializer
    queryset = FoodCategory.objects.all()


@_tag_readonly_viewset("Super Admin - Orders")
class SuperAdminOrderViewSet(SuperAdminReadOnlyViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("customer", "courier", "restaurant", "branch").all()


@_tag_viewset("Restaurant Admin - Branch Admins")
class RestaurantAdminBranchAdminUserViewSet(RestaurantAdminBaseViewSet):
    serializer_class = RestaurantAdminBranchAdminUserSerializer
    queryset = User.objects.all()

    def get_queryset(self):
        user = self.request.user
        if user.role != User.RoleChoices.RESTAURANT_ADMIN:
            return User.objects.none()

        allowed_branches = self.get_allowed_branches()
        return User.objects.filter(
            Q(role=User.RoleChoices.BRANCH_ADMIN, managed_branches__in=allowed_branches) | Q(pk=user.pk)
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

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Only super admin can create food categories."},
            status=status.HTTP_403_FORBIDDEN,
        )


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


@_tag_readonly_viewset("Restaurant Admin - Orders")
class RestaurantAdminOrderViewSet(RestaurantAdminReadOnlyViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("customer", "courier", "restaurant", "branch").all()

    def get_queryset(self):
        return Order.objects.select_related("customer", "courier", "restaurant", "branch").filter(
            restaurant__in=self.request.user.managed_restaurants.all()
        )


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

    def create(self, request, *args, **kwargs):
        return Response(
            {"detail": "Only super admin can create food categories."},
            status=status.HTTP_403_FORBIDDEN,
        )


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


@_tag_readonly_viewset("Branch Admin - Orders")
class BranchAdminOrderViewSet(BranchAdminReadOnlyViewSet):
    serializer_class = OrderSerializer
    queryset = Order.objects.select_related("customer", "courier", "restaurant", "branch").all()

    def get_queryset(self):
        return Order.objects.select_related("customer", "courier", "restaurant", "branch").filter(
            branch__in=self.request.user.managed_branches.all()
        )
