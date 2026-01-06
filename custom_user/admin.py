from django.contrib import admin
from django.contrib.admin import AdminSite

from custom_user.models import *
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
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')


@admin.register(RestaurantBranches, site=custom_super_admin_site)
class RestaurantBranchesAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'address', 'state', 'status')


