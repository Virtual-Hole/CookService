from rest_framework import serializers
from drf_spectacular.utils import extend_schema_field
from drf_spectacular.types import OpenApiTypes
from foods.models import FoodCategory, Food, FoodMenuBranchCollection, FoodMenuBranch
from restaurants.models import RestaurantBranches


class FoodCategorySerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = FoodCategory
        fields = ('id', 'branch', 'branch_name', 'name', 'created_at')
        read_only_fields = ('id', 'created_at')


class FoodSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    discounted_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    image_url = serializers.SerializerMethodField()
    
    class Meta:
        model = Food
        fields = (
            'id', 'name', 'price', 'image', 'image_url', 'description',
            'category', 'category_name', 'branch_name', 'discount_percent',
            'discount_active', 'discounted_price', 'created_at', 'updated_at'
        )
        read_only_fields = ('id', 'created_at', 'updated_at')
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_image_url(self, obj):
        if obj.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.image.url)
            return obj.image.url
        return None


class FoodMenuBranchCollectionSerializer(serializers.ModelSerializer):
    branch_name = serializers.CharField(source='branch.name', read_only=True)
    
    class Meta:
        model = FoodMenuBranchCollection
        fields = ('id', 'branch', 'branch_name', 'name', 'description', 'is_active', 'created_at')
        read_only_fields = ('id', 'created_at')


class FoodMenuBranchSerializer(serializers.ModelSerializer):
    food_name = serializers.CharField(source='food.name', read_only=True)
    food_price = serializers.DecimalField(source='food.price', max_digits=10, decimal_places=2, read_only=True)
    food_image = serializers.SerializerMethodField()
    collection_name = serializers.CharField(source='collection.name', read_only=True)
    
    class Meta:
        model = FoodMenuBranch
        fields = (
            'id', 'food', 'food_name', 'food_price', 'food_image',
            'collection', 'collection_name', 'is_available', 'added_at'
        )
        read_only_fields = ('id', 'added_at')
    
    @extend_schema_field(OpenApiTypes.URI)
    def get_food_image(self, obj):
        if obj.food.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.food.image.url)
            return obj.food.image.url
        return None


class FoodCategoryCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodCategory
        fields = ('branch', 'name')


class FoodCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Food
        fields = (
            'name', 'price', 'image', 'description',
            'category', 'discount_percent', 'discount_active'
        )


class FoodMenuBranchCollectionCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodMenuBranchCollection
        fields = ('branch', 'name', 'description', 'is_active')


class FoodMenuBranchCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FoodMenuBranch
        fields = ('food', 'collection', 'is_available')

