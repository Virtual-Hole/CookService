from django.urls import path
from foods.views import (
    # FoodCategory
    FoodCategoryListView,
    FoodCategoryCreateView,
    FoodCategoryDetailView,
    
    # Food
    FoodListView,
    FoodCreateView,
    FoodDetailView,
    
    # FoodMenuBranchCollection
    FoodMenuBranchCollectionListView,
    FoodMenuBranchCollectionCreateView,
    FoodMenuBranchCollectionDetailView,
    
    # FoodMenuBranch
    FoodMenuBranchListView,
    FoodMenuBranchCreateView,
    FoodMenuBranchDetailView,
)

urlpatterns = [
    # FoodCategory endpoints
    path('categories/', FoodCategoryListView.as_view(), name='food-category-list'),
    path('categories/create/', FoodCategoryCreateView.as_view(), name='food-category-create'),
    path('categories/<int:id>/', FoodCategoryDetailView.as_view(), name='food-category-detail'),
    
    # Food endpoints
    path('foods/', FoodListView.as_view(), name='food-list'),
    path('foods/create/', FoodCreateView.as_view(), name='food-create'),
    path('foods/<int:id>/', FoodDetailView.as_view(), name='food-detail'),
    
    # FoodMenuBranchCollection endpoints
    path('menu-collections/', FoodMenuBranchCollectionListView.as_view(), name='menu-collection-list'),
    path('menu-collections/create/', FoodMenuBranchCollectionCreateView.as_view(), name='menu-collection-create'),
    path('menu-collections/<int:id>/', FoodMenuBranchCollectionDetailView.as_view(), name='menu-collection-detail'),
    
    # FoodMenuBranch endpoints
    path('menu-branches/', FoodMenuBranchListView.as_view(), name='menu-branch-list'),
    path('menu-branches/create/', FoodMenuBranchCreateView.as_view(), name='menu-branch-create'),
    path('menu-branches/<int:id>/', FoodMenuBranchDetailView.as_view(), name='menu-branch-detail'),
]

