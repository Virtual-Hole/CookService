from django.contrib.auth import get_user_model
from rest_framework import serializers

from custom_user.models import VehicleType
from foods.models import FoodCategory
from foods.serializers import (
    FoodCategorySerializer,
    FoodSerializer,
    FoodMenuBranchCollectionSerializer,
    FoodMenuBranchSerializer,
)
from restaurants.models import Order, Restaurants, RestaurantBranches


User = get_user_model()


def _branch_ids(allowed_branches):
    if allowed_branches is None:
        return None
    return set(allowed_branches.values_list("id", flat=True))


class RestaurantAdminRestaurantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Restaurants
        fields = (
            "id",
            "uid",
            "name",
            "logo",
            "phone",
            "email",
            "description",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class SuperAdminRestaurantSerializer(serializers.ModelSerializer):
    hasAdmin = serializers.SerializerMethodField()

    class Meta:
        model = Restaurants
        fields = (
            "id",
            "uid",
            "name",
            "logo",
            "phone",
            "email",
            "description",
            "hasAdmin",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "uid", "created_at", "updated_at", "hasAdmin")

    def get_hasAdmin(self, obj):
        return obj.admins.filter(role=User.RoleChoices.RESTAURANT_ADMIN).exists()


class SuperAdminRestaurantAdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "uid",
            "email",
            "phone_number",
            "full_name",
            "password",
            "profile_photo",
            "managed_restaurants",
            "is_active",
            "role",
        )
        read_only_fields = ("id", "uid", "role")

    def validate_managed_restaurants(self, value):
        if not value:
            raise serializers.ValidationError("At least one restaurant is required.")
        return value

    def validate(self, data):
        if self.instance is None:
            if not self.initial_data.get("password"):
                raise serializers.ValidationError({"password": "Password is required."})
            if not self.initial_data.get("managed_restaurants"):
                raise serializers.ValidationError({"managed_restaurants": "At least one restaurant is required."})
        return data

    def create(self, validated_data):
        restaurants = validated_data.pop("managed_restaurants", [])
        password = validated_data.pop("password", None)
        profile_photo = validated_data.pop("profile_photo", None)

        user = User(
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            full_name=validated_data.get("full_name", ""),
            is_active=validated_data.get("is_active", True),
            role=User.RoleChoices.RESTAURANT_ADMIN,
            is_staff=True,
        )
        user.set_password(password)
        if profile_photo:
            user.profile_photo = profile_photo
        user.save()
        user.managed_restaurants.set(restaurants)
        user.managed_branches.clear()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        restaurants = validated_data.pop("managed_restaurants", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)
        instance.save()

        if restaurants is not None:
            instance.managed_restaurants.set(restaurants)
            instance.managed_branches.clear()

        return instance


class SuperAdminCourierSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "uid",
            "courier_id",
            "email",
            "phone_number",
            "full_name",
            "password",
            "profile_photo",
            "managed_branches",
            "is_active",
            "role",
        )
        read_only_fields = ("id", "uid", "courier_id", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["managed_branches"].queryset = RestaurantBranches.objects.all()

    def validate(self, data):
        if self.instance is None and not self.initial_data.get("password"):
            raise serializers.ValidationError({"password": "Password is required."})
        return data

    def create(self, validated_data):
        branches = validated_data.pop("managed_branches", [])
        password = validated_data.pop("password", None)
        profile_photo = validated_data.pop("profile_photo", None)

        user = User(
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            full_name=validated_data.get("full_name", ""),
            is_active=validated_data.get("is_active", True),
            role=User.RoleChoices.COURIER,
            is_staff=False,
        )
        user.set_password(password)
        if profile_photo:
            user.profile_photo = profile_photo
        user.save()
        user.managed_branches.set(branches)
        user.managed_restaurants.clear()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        branches = validated_data.pop("managed_branches", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)
        instance.save()

        if branches is not None:
            instance.managed_branches.set(branches)
            instance.managed_restaurants.clear()

        return instance


class SuperAdminFoodCategorySerializer(serializers.ModelSerializer):
    logo = serializers.ImageField(required=True)

    class Meta:
        model = FoodCategory
        fields = (
            "id",
            "uid",
            "name",
            "logo",
            "created_at",
        )
        read_only_fields = ("id", "uid", "created_at")


class RestaurantAdminBranchSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantBranches
        fields = (
            "id",
            "uid",
            "restaurant",
            "name",
            "latitude",
            "longitude",
            "address",
            "email",
            "phone",
            "start_time",
            "close_time",
            "state",
            "status",
            "delivery_time",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "uid", "created_at", "updated_at")


class RestaurantAdminBranchAdminUserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "uid",
            "email",
            "phone_number",
            "full_name",
            "password",
            "profile_photo",
            "managed_branches",
            "is_active",
            "role",
        )
        read_only_fields = ("id", "uid", "role")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        allowed_branches = self.context.get("allowed_branches")
        if allowed_branches is not None:
            self.fields["managed_branches"].queryset = allowed_branches

    def validate_managed_branches(self, value):
        if not value:
            raise serializers.ValidationError("At least one branch is required.")

        allowed = self.context.get("allowed_branches")
        allowed_ids = _branch_ids(allowed)
        if allowed_ids is not None:
            invalid = [branch.id for branch in value if branch.id not in allowed_ids]
            if invalid:
                raise serializers.ValidationError("Branch is not allowed.")

        return value

    def validate(self, data):
        request = self.context.get("request")
        if self.instance is None:
            if not self.initial_data.get("password"):
                raise serializers.ValidationError({"password": "Password is required."})
            if not self.initial_data.get("managed_branches"):
                raise serializers.ValidationError({"managed_branches": "At least one branch is required."})
        elif request and self.instance.pk == request.user.pk and "managed_branches" in data:
            raise serializers.ValidationError(
                {"managed_branches": "You cannot update managed branches for yourself."}
            )
        return data

    def create(self, validated_data):
        branches = validated_data.pop("managed_branches", [])
        password = validated_data.pop("password", None)
        profile_photo = validated_data.pop("profile_photo", None)

        user = User(
            email=validated_data.get("email"),
            phone_number=validated_data.get("phone_number"),
            full_name=validated_data.get("full_name", ""),
            is_active=validated_data.get("is_active", True),
            role=User.RoleChoices.BRANCH_ADMIN,
            is_staff=True,
        )
        user.set_password(password)
        if profile_photo:
            user.profile_photo = profile_photo
        user.save()
        user.managed_branches.set(branches)
        user.managed_restaurants.clear()
        return user

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        branches = validated_data.pop("managed_branches", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)
        instance.save()

        if branches is not None:
            instance.managed_branches.set(branches)

        return instance


class BranchAdminSelfSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(read_only=True)
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            "id",
            "uid",
            "email",
            "phone_number",
            "full_name",
            "password",
            "is_active",
            "role",
        )
        read_only_fields = ("id", "uid", "role")

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)

        for field, value in validated_data.items():
            setattr(instance, field, value)

        if password:
            instance.set_password(password)
        instance.save()
        return instance


class VehicleTypeSerializer(serializers.ModelSerializer):
    user_uid = serializers.UUIDField(source="user.uid", read_only=True)

    class Meta:
        model = VehicleType
        fields = (
            "id",
            "uid",
            "user",
            "user_uid",
            "name",
            "min_km",
            "max_km",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "uid", "created_at", "updated_at", "user_uid")

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = User.objects.filter(role=User.RoleChoices.COURIER)

    def validate(self, attrs):
        min_km = attrs.get("min_km", getattr(self.instance, "min_km", None))
        max_km = attrs.get("max_km", getattr(self.instance, "max_km", None))
        user = attrs.get("user", getattr(self.instance, "user", None))

        if min_km is not None and max_km is not None and max_km < min_km:
            raise serializers.ValidationError({"max_km": "max_km must be greater than or equal to min_km."})

        if user and user.role != User.RoleChoices.COURIER:
            raise serializers.ValidationError({"user": "Vehicle type user must be a courier."})

        return attrs


class OrderSerializer(serializers.ModelSerializer):
    customer_uid = serializers.UUIDField(source="customer.uid", read_only=True)
    courier_uid = serializers.UUIDField(source="courier.uid", read_only=True)
    restaurant_uid = serializers.UUIDField(source="restaurant.uid", read_only=True)
    branch_uid = serializers.UUIDField(source="branch.uid", read_only=True)

    class Meta:
        model = Order
        fields = (
            "id",
            "uid",
            "customer",
            "customer_uid",
            "courier",
            "courier_uid",
            "restaurant",
            "restaurant_uid",
            "branch",
            "branch_uid",
            "total_amount",
            "status",
            "note",
            "created_at",
            "updated_at",
        )
        read_only_fields = fields


class AdminFoodCategorySerializer(FoodCategorySerializer):
    def validate_branch(self, branch):
        allowed = self.context.get("allowed_branches")
        if branch and allowed is not None and not allowed.filter(pk=branch.pk).exists():
            raise serializers.ValidationError("Branch is not allowed.")
        return branch


class AdminFoodSerializer(FoodSerializer):
    def validate_category(self, category):
        allowed = self.context.get("allowed_branches")
        if allowed is not None and category.branch_id and not allowed.filter(pk=category.branch_id).exists():
            raise serializers.ValidationError("Category is not allowed.")
        return category


class AdminFoodMenuBranchCollectionSerializer(FoodMenuBranchCollectionSerializer):
    def validate_branch(self, branch):
        allowed = self.context.get("allowed_branches")
        if allowed is not None and not allowed.filter(pk=branch.pk).exists():
            raise serializers.ValidationError("Branch is not allowed.")
        return branch


class AdminFoodMenuBranchSerializer(FoodMenuBranchSerializer):
    def validate(self, data):
        data = super().validate(data)
        allowed = self.context.get("allowed_branches")
        if allowed is None:
            return data

        collection = data.get("collection") or getattr(self.instance, "collection", None)
        food = data.get("food") or getattr(self.instance, "food", None)

        if collection and not allowed.filter(pk=collection.branch_id).exists():
            raise serializers.ValidationError({"collection": "Collection is not allowed."})

        food_branch_id = food.category.branch_id if food and food.category_id else None
        if food_branch_id and not allowed.filter(pk=food_branch_id).exists():
            raise serializers.ValidationError({"food": "Food is not allowed."})

        return data
