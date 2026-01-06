from django import forms
from django.contrib import admin
from django.db import models
from django.db.models import Q

from custom_user.models import CustomUser
from restaurants.models import Restaurants, RestaurantBranches


class CustomRestaurantAdminSite(admin.AdminSite):
    site_header = "Restaurant Admin"
    site_title = "Restaurant Admin"
    index_title = "Restaurant Dashboard"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated

    def index(self, request, extra_context=None):
        if not (hasattr(request.user, 'role') and request.user.role == 'restaurant_admin'):
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), self.login_url)
        return super().index(request, extra_context)


custom_restaurant_admin_site = CustomRestaurantAdminSite(name='restaurant_admin')


class BranchAdminUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'phone_number', 'profile_photo', 'password', 'managed_branches', 'is_active')

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        self.fields['password'].widget = forms.PasswordInput()

        if self.request and self.request.user.role == 'restaurant_admin':
            my_restaurants = self.request.user.managed_restaurants.all()
            self.fields['managed_branches'].queryset = RestaurantBranches.objects.filter(
                restaurant__in=my_restaurants
            )
            self.fields['managed_branches'].required = True

    def clean_managed_branches(self):
        branches = self.cleaned_data.get('managed_branches')
        if not branches or branches.count() == 0:
            raise forms.ValidationError('Kamida bitta branch tanlash majburiy!')
        return branches

    def clean(self):
        cleaned_data = super().clean()

        if self.request and self.request.user.role == 'restaurant_admin':
            branches = cleaned_data.get('managed_branches')
            if not branches:
                raise forms.ValidationError('Branch tanlash majburiy!')

        return cleaned_data


@admin.register(CustomUser, site=custom_restaurant_admin_site)
class RestaurantAdminUserAdmin(admin.ModelAdmin):
    form = BranchAdminUserForm
    list_display = ('email', 'full_name', 'get_branches', 'is_active')
    list_filter = ('is_active',)

    fields = ('email', 'full_name', 'phone_number', 'password', 'profile_photo', 'managed_branches', 'is_active')
    filter_horizontal = ('managed_branches',)

    def get_branches(self, obj):
        branches = obj.managed_branches.all()
        return ", ".join([b.name for b in branches]) if branches else "-"

    get_branches.short_description = 'Branches'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            my_restaurants = request.user.managed_restaurants.all()
            my_branches = RestaurantBranches.objects.filter(restaurant__in=my_restaurants)

            return qs.filter(
                Q(role='branch_admin', managed_branches__in=my_branches) |
                Q(pk=request.user.pk)
            ).distinct()
        return qs

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk == request.user.pk:
            return ('role', 'managed_restaurants', 'managed_branches')
        return ()

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "managed_branches" and request.user.role == 'restaurant_admin':
            my_restaurants = request.user.managed_restaurants.all()
            kwargs["queryset"] = RestaurantBranches.objects.filter(restaurant__in=my_restaurants)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def save_model(self, request, obj, form, change):

        if change and obj.pk == request.user.pk:
            if 'password' in form.changed_data:
                obj.set_password(obj.password)
            super().save_model(request, obj, form, change)
            return

        if not change:
            obj.set_password(obj.password)
            obj.role = 'branch_admin'
            obj.is_staff = True
        elif 'password' in form.changed_data:
            obj.set_password(obj.password)

        obj.role = 'branch_admin'

        super().save_model(request, obj, form, change)

        obj.managed_restaurants.clear()

    def has_add_permission(self, request):
        return request.user.role == 'restaurant_admin'

    def has_change_permission(self, request, obj=None):
        if obj:
            if obj.pk == request.user.pk:
                return True

            if request.user.role == 'restaurant_admin':
                my_restaurants = request.user.managed_restaurants.all()
                user_branches = obj.managed_branches.all()
                return user_branches.filter(restaurant__in=my_restaurants).exists()
        return True

    def has_delete_permission(self, request, obj=None):
        if obj and obj.pk == request.user.pk:
            return False

        if obj and request.user.role == 'restaurant_admin':
            my_restaurants = request.user.managed_restaurants.all()
            user_branches = obj.managed_branches.all()
            return user_branches.filter(restaurant__in=my_restaurants).exists()
        return True

    def has_view_permission(self, request, obj=None):
        if obj:
            if obj.pk == request.user.pk:
                return True

            if request.user.role == 'restaurant_admin':
                my_restaurants = request.user.managed_restaurants.all()
                user_branches = obj.managed_branches.all()
                return user_branches.filter(restaurant__in=my_restaurants).exists()
        return True


@admin.register(Restaurants, site=custom_restaurant_admin_site)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    exclude = ('admins',)

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            return qs.filter(admins=request.user)
        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


class RestaurantBranchForm(forms.ModelForm):
    class Meta:
        model = RestaurantBranches
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        if not self.instance.pk and self.request and self.request.user.role == 'restaurant_admin':
            if 'restaurant' in self.fields:
                my_restaurants = self.request.user.managed_restaurants.all()
                if my_restaurants.exists():
                    self.fields['restaurant'].initial = my_restaurants.first()
                    self.fields['restaurant'].widget = forms.HiddenInput()
                    self.fields['restaurant'].required = False


@admin.register(RestaurantBranches, site=custom_restaurant_admin_site)
class RestaurantAdminBranchesAdmin(admin.ModelAdmin):
    form = RestaurantBranchForm
    list_display = ('name', 'restaurant', 'address', 'status')

    def get_form(self, request, obj=None, **kwargs):
        FormClass = super().get_form(request, obj, **kwargs)

        class FormWithRequest(FormClass):
            def __new__(cls, *args, **kwargs):
                kwargs['request'] = request
                return FormClass(*args, **kwargs)

        return FormWithRequest

    def get_readonly_fields(self, request, obj=None):
        if obj and request.user.role == 'restaurant_admin':
            return ('restaurant',)
        return ()

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            return qs.filter(restaurant__admins=request.user)
        return qs

    def save_model(self, request, obj, form, change):
        if not change and request.user.role == 'restaurant_admin':
            if not obj.restaurant:
                my_restaurants = request.user.managed_restaurants.all()
                if my_restaurants.exists():
                    obj.restaurant = my_restaurants.first()
        super().save_model(request, obj, form, change)

    def has_change_permission(self, request, obj=None):
        if obj and request.user.role == 'restaurant_admin':
            return request.user in obj.restaurant.admins.all()
        return True

    def has_delete_permission(self, request, obj=None):
        if obj and request.user.role == 'restaurant_admin':
            return request.user in obj.restaurant.admins.all()
        return True

# # Restaurant Admin o'z kategoriyalarini boshqaradi
# @admin.register(Category, site=custom_restaurant_admin_site)
# class RestaurantAdminCategoryAdmin(admin.ModelAdmin):
#     list_display = ('name', 'restaurant')
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.role == 'restaurant_admin':
#             return qs.filter(restaurant__admins=request.user)
#         return qs
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if db_field.name == "restaurant" and request.user.role == 'restaurant_admin':
#             kwargs["queryset"] = Restaurants.objects.filter(admins=request.user)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
#
#     def has_change_permission(self, request, obj=None):
#         if obj and request.user.role == 'restaurant_admin':
#             return request.user in obj.restaurant.admins.all()
#         return True
#
#     def has_delete_permission(self, request, obj=None):
#         if obj and request.user.role == 'restaurant_admin':
#             return request.user in obj.restaurant.admins.all()
#         return True
#
#
# # Restaurant Admin barcha branch'laridagi ovqatlarni ko'radi
# @admin.register(Food, site=custom_restaurant_admin_site)
# class RestaurantAdminFoodAdmin(admin.ModelAdmin):
#     list_display = ('name', 'branch', 'category', 'price')
#     list_filter = ('branch', 'category')
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.role == 'restaurant_admin':
#             my_restaurants = request.user.managed_restaurants.all()
#             return qs.filter(branch__restaurant__in=my_restaurants)
#         return qs
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if request.user.role == 'restaurant_admin':
#             my_restaurants = request.user.managed_restaurants.all()
#             if db_field.name == "branch":
#                 kwargs["queryset"] = RestaurantBranches.objects.filter(restaurant__in=my_restaurants)
#             elif db_field.name == "category":
#                 kwargs["queryset"] = Category.objects.filter(restaurant__in=my_restaurants)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)

class CustomBranchAdminSite(admin.AdminSite):
    site_header = "Branch Admin"
    site_title = "Branch Admin"
    index_title = "Branch Dashboard"

    def has_permission(self, request):
        return request.user.is_active and request.user.is_authenticated

    def index(self, request, extra_context=None):
        if not (hasattr(request.user, 'role') and request.user.role == 'branch_admin'):
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path(), self.login_url)
        return super().index(request, extra_context)


custom_branch_admin_site = CustomBranchAdminSite(name='branch_admin')


@admin.register(RestaurantBranches, site=custom_branch_admin_site)
class BranchAdminBranchesAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'address', 'status')
    readonly_fields = ('restaurant', 'name', 'address', 'latitude', 'longitude', )

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            return qs.filter(admins=request.user)
        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# # Branch Admin faqat o'z branch'idagi ovqatlarni boshqaradi
# @admin.register(Food, site=custom_branch_admin_site)
# class BranchAdminFoodAdmin(admin.ModelAdmin):
#     list_display = ('name', 'category', 'price', 'branch')
#     list_filter = ('category',)
#
#     def get_queryset(self, request):
#         qs = super().get_queryset(request)
#         if request.user.role == 'branch_admin':
#             my_branches = request.user.managed_branches.all()
#             return qs.filter(branch__in=my_branches)
#         return qs
#
#     def formfield_for_foreignkey(self, db_field, request, **kwargs):
#         if request.user.role == 'branch_admin':
#             my_branches = request.user.managed_branches.all()
#             if db_field.name == "branch":
#                 kwargs["queryset"] = my_branches
#             elif db_field.name == "category":
#                 # Faqat o'z restaurant'ining kategoriyalari
#                 my_restaurant_ids = my_branches.values_list('restaurant_id', flat=True)
#                 kwargs["queryset"] = Category.objects.filter(restaurant_id__in=my_restaurant_ids)
#         return super().formfield_for_foreignkey(db_field, request, **kwargs)
#
#     def has_change_permission(self, request, obj=None):
#         if obj and request.user.role == 'branch_admin':
#             return obj.branch in request.user.managed_branches.all()
#         return True
#
#     def has_delete_permission(self, request, obj=None):
#         if obj and request.user.role == 'branch_admin':
#             return obj.branch in request.user.managed_branches.all()
#         return True