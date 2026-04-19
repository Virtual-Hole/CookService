from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.html import format_html

from custom_user.models import *
from foods.models import *
from restaurants.models import *


class CustomAdminSite(AdminSite):
    site_header = "Cook Delivery"
    site_title = "Cook Delivery Admin"
    index_title = "Cook Delivery Dashboard"

    def get_urls(self):
        urls = super().get_urls()
        return urls

    def has_permission(self, request):
        return (
                request.user.is_active
                and request.user.is_authenticated
                and hasattr(request.user, 'role')
                and request.user.role == 'super_admin'
        )


custom_super_admin_site = CustomAdminSite(name='super_admin')


@admin.register(CustomUser, site=custom_super_admin_site)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'phone_number', 'full_name', 'role', 'is_staff')
    list_filter = ('role', 'is_active')
    filter_horizontal = ('managed_restaurants', 'managed_branches')

    def save_model(self, request, obj, form, change):
        if not change:
            obj.set_password(obj.password)

        super().save_model(request, obj, form, change)


@admin.register(Card, site=custom_super_admin_site)
class CardAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'default')


@admin.register(Address, site=custom_super_admin_site)
class AddressAdmin(admin.ModelAdmin):
    list_display = ('name', 'user', 'address', 'default')


@admin.register(Device, site=custom_super_admin_site)
class DeviceAdmin(admin.ModelAdmin):
    list_display = ('device_name', 'user', 'location_city')


@admin.register(Restaurants, site=custom_super_admin_site)
class SuperAdminRestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'get_admins_count', 'get_branches_count', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('name', 'email', 'phone')

    def get_admins_count(self, obj):
        count = obj.admins.count()
        return format_html('<b>{}</b> admins', count)

    get_admins_count.short_description = 'Admins'

    def get_branches_count(self, obj):
        count = obj.branches.count()
        return format_html('<b>{}</b> branches', count)

    get_branches_count.short_description = 'Branches'


@admin.register(RestaurantBranches, site=custom_super_admin_site)
class SuperAdminBranchesAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'address', 'state', 'status', 'get_categories_count', 'get_collections_count')
    list_filter = ('status', 'state', 'restaurant')
    search_fields = ('name', 'address')

    def get_categories_count(self, obj):
        count = obj.food_categories.count()
        return format_html('<b>{}</b> categories', count)

    get_categories_count.short_description = 'Categories'

    def get_collections_count(self, obj):
        count = obj.menu_collections.count()
        return format_html('<b>{}</b> menus', count)

    get_collections_count.short_description = 'Menu Collections'


@admin.register(FoodCategory, site=custom_super_admin_site)
class SuperAdminFoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'get_restaurant', 'get_foods_count', 'created_at')
    list_filter = ('branch__restaurant', 'branch')
    search_fields = ('name', 'branch__name', 'branch__restaurant__name')

    def get_restaurant(self, obj):
        if obj.branch_id:
            return obj.branch.restaurant.name
        return "-"

    get_restaurant.short_description = 'Restaurant'

    def get_foods_count(self, obj):
        count = obj.foods.count()
        return format_html('<b>{}</b> foods', count)

    get_foods_count.short_description = 'Foods'


@admin.register(Food, site=custom_super_admin_site)
class SuperAdminFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_branch', 'price', 'get_discount_info', 'get_image_preview', 'created_at')
    list_filter = ('category__branch__restaurant', 'category__branch', 'category', 'discount_active')
    search_fields = ('name', 'description', 'category__name')

    readonly_fields = ('created_at', 'updated_at')

    def get_branch(self, obj):
        return obj.category.branch.name

    get_branch.short_description = 'Branch'

    def get_discount_info(self, obj):
        if obj.discount_active and obj.discount_percent > 0:
            return format_html(
                '<span style="color: red; font-weight: bold;">-{}% (${:.2f})</span>',
                obj.discount_percent,
                obj.discounted_price
            )
        return '-'

    get_discount_info.short_description = 'Discount'

    def get_image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                               obj.image.url)
        return '-'

    get_image_preview.short_description = 'Image'


@admin.register(FoodMenuBranchCollection, site=custom_super_admin_site)
class SuperAdminMenuCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'get_restaurant', 'is_active', 'get_foods_count', 'created_at')
    list_filter = ('is_active', 'branch__restaurant', 'branch')
    search_fields = ('name', 'description', 'branch__name')

    def get_restaurant(self, obj):
        return obj.branch.restaurant.name

    get_restaurant.short_description = 'Restaurant'

    def get_foods_count(self, obj):
        count = obj.food_items.count()
        return format_html('<b>{}</b> foods', count)

    get_foods_count.short_description = 'Foods in Menu'


@admin.register(FoodMenuBranch, site=custom_super_admin_site)
class SuperAdminFoodMenuBranchAdmin(admin.ModelAdmin):
    list_display = ('food', 'collection', 'get_branch', 'is_available', 'added_at')
    list_filter = ('is_available', 'collection__branch__restaurant', 'collection__branch', 'collection')
    search_fields = ('food__name', 'collection__name')

    def get_branch(self, obj):
        return obj.collection.branch.name

    get_branch.short_description = 'Branch'

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "food":
            pass
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

