from django.urls import include, path
from rest_framework.routers import DefaultRouter

from admin_api.views import (
    BranchAdminBranchViewSet,
    SuperAdminBranchAdminUserViewSet,
    SuperAdminBranchViewSet,
    SuperAdminCourierViewSet,
    SuperAdminFoodCategoryViewSet,
    SuperAdminOrderViewSet,
    SuperAdminRestaurantAdminUserViewSet,
    SuperAdminRestaurantViewSet,
    SuperAdminVehicleTypeViewSet,
    BranchAdminFoodCategoryViewSet,
    BranchAdminFoodViewSet,
    BranchAdminMenuBranchViewSet,
    BranchAdminMenuCollectionViewSet,
    BranchAdminOrderViewSet,
    BranchAdminProfileView,
    RestaurantAdminBranchAdminUserViewSet,
    RestaurantAdminBranchViewSet,
    RestaurantAdminFoodCategoryViewSet,
    RestaurantAdminFoodViewSet,
    RestaurantAdminMenuBranchViewSet,
    RestaurantAdminMenuCollectionViewSet,
    RestaurantAdminOrderViewSet,
    RestaurantAdminRestaurantViewSet,
)


router = DefaultRouter()

router.register(
    r"super/restaurants",
    SuperAdminRestaurantViewSet,
    basename="super-admin-restaurants",
)
router.register(
    r"super/branches",
    SuperAdminBranchViewSet,
    basename="super-admin-branches",
)
router.register(
    r"super/restaurant-admins",
    SuperAdminRestaurantAdminUserViewSet,
    basename="super-admin-restaurant-admins",
)
router.register(
    r"super/branch-admins",
    SuperAdminBranchAdminUserViewSet,
    basename="super-admin-branch-admins",
)
router.register(
    r"super/couriers",
    SuperAdminCourierViewSet,
    basename="super-admin-couriers",
)
router.register(
    r"super/vehicle-types",
    SuperAdminVehicleTypeViewSet,
    basename="super-admin-vehicle-types",
)
router.register(
    r"super/food-categories",
    SuperAdminFoodCategoryViewSet,
    basename="super-admin-food-categories",
)
router.register(
    r"super/orders",
    SuperAdminOrderViewSet,
    basename="super-admin-orders",
)

router.register(
    r"restaurant/branch-admins",
    RestaurantAdminBranchAdminUserViewSet,
    basename="restaurant-admin-branch-admins",
)
router.register(
    r"restaurant/restaurants",
    RestaurantAdminRestaurantViewSet,
    basename="restaurant-admin-restaurants",
)
router.register(
    r"restaurant/branches",
    RestaurantAdminBranchViewSet,
    basename="restaurant-admin-branches",
)
router.register(
    r"restaurant/food-categories",
    RestaurantAdminFoodCategoryViewSet,
    basename="restaurant-admin-food-categories",
)
router.register(
    r"restaurant/foods",
    RestaurantAdminFoodViewSet,
    basename="restaurant-admin-foods",
)
router.register(
    r"restaurant/menu-collections",
    RestaurantAdminMenuCollectionViewSet,
    basename="restaurant-admin-menu-collections",
)
router.register(
    r"restaurant/menu-branches",
    RestaurantAdminMenuBranchViewSet,
    basename="restaurant-admin-menu-branches",
)
router.register(
    r"restaurant/orders",
    RestaurantAdminOrderViewSet,
    basename="restaurant-admin-orders",
)

router.register(
    r"branch/branches",
    BranchAdminBranchViewSet,
    basename="branch-admin-branches",
)
router.register(
    r"branch/food-categories",
    BranchAdminFoodCategoryViewSet,
    basename="branch-admin-food-categories",
)
router.register(
    r"branch/foods",
    BranchAdminFoodViewSet,
    basename="branch-admin-foods",
)
router.register(
    r"branch/menu-collections",
    BranchAdminMenuCollectionViewSet,
    basename="branch-admin-menu-collections",
)
router.register(
    r"branch/menu-branches",
    BranchAdminMenuBranchViewSet,
    basename="branch-admin-menu-branches",
)
router.register(
    r"branch/orders",
    BranchAdminOrderViewSet,
    basename="branch-admin-orders",
)


urlpatterns = [
    path("", include(router.urls)),
    path("branch/me/", BranchAdminProfileView.as_view(), name="branch-admin-me"),
]
