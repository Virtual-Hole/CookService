from django.urls import path
from foods.views import (
    # FoodCategory
    FoodCategoryListView,
    FoodCategoryDetailView,
    
    # Food
    FoodListView,
    FoodDetailView,
    
    # FoodMenuBranchCollection
    FoodMenuBranchCollectionListView,
    FoodMenuBranchCollectionDetailView,
    
    # FoodMenuBranch
    FoodMenuBranchListView,
    FoodMenuBranchDetailView,
)

urlpatterns = [
    # FoodCategory endpoints
    path('categories/', FoodCategoryListView.as_view(), name='food-category-list'),
    path('categories/<int:id>/', FoodCategoryDetailView.as_view(), name='food-category-detail'),
    
    # Food endpoints
    path('foods/', FoodListView.as_view(), name='food-list'),
    path('foods/<int:id>/', FoodDetailView.as_view(), name='food-detail'),
    
    # FoodMenuBranchCollection endpoints
    path('menu-collections/', FoodMenuBranchCollectionListView.as_view(), name='menu-collection-list'),
    path('menu-collections/<int:id>/', FoodMenuBranchCollectionDetailView.as_view(), name='menu-collection-detail'),
    
    # FoodMenuBranch endpoints
    path('menu-branches/', FoodMenuBranchListView.as_view(), name='menu-branch-list'),
    path('menu-branches/<int:id>/', FoodMenuBranchDetailView.as_view(), name='menu-branch-detail'),
]
