from django.urls import include, path
from rest_framework.routers import DefaultRouter

from admin_api.views import (
    BranchAdminBranchViewSet,
    SuperAdminBranchAdminUserViewSet,
    SuperAdminBranchViewSet,
    SuperAdminRestaurantAdminUserViewSet,
    SuperAdminRestaurantViewSet,
    BranchAdminFoodCategoryViewSet,
    BranchAdminFoodViewSet,
    BranchAdminMenuBranchViewSet,
    BranchAdminMenuCollectionViewSet,
    BranchAdminProfileView,
    RestaurantAdminBranchAdminUserViewSet,
    RestaurantAdminBranchViewSet,
    RestaurantAdminFoodCategoryViewSet,
    RestaurantAdminFoodViewSet,
    RestaurantAdminMenuBranchViewSet,
    RestaurantAdminMenuCollectionViewSet,
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


urlpatterns = [
    path("", include(router.urls)),
    path("branch/me/", BranchAdminProfileView.as_view(), name="branch-admin-me"),
]
