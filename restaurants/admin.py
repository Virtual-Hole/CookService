# restaurants/admin.py (Restaurant Admin site uchun)

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Q
from django import forms
from custom_user.models import CustomUser
from restaurants.models import Restaurants, RestaurantBranches
from foods.models import FoodCategory, Food, FoodMenuBranchCollection, FoodMenuBranch


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


# =====================================================
# HELPER: O'z restaurant'larini olish
# =====================================================
def get_my_restaurants(request):
    """Request user'ning restaurant'larini qaytaradi"""
    if request.user.role == 'restaurant_admin':
        return request.user.managed_restaurants.all()
    return Restaurants.objects.none()


def get_my_branches(request):
    """Request user'ning branch'larini qaytaradi"""
    my_restaurants = get_my_restaurants(request)
    return RestaurantBranches.objects.filter(restaurant__in=my_restaurants)


# =====================================================
# 1. BRANCH ADMIN USER MANAGEMENT
# =====================================================
class BranchAdminUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'phone_number', 'password', 'profile_photo', 'managed_branches', 'is_active')

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


@admin.register(CustomUser, site=custom_restaurant_admin_site)
class RestaurantAdminUserAdmin(admin.ModelAdmin):
    form = BranchAdminUserForm
    list_display = ('email', 'full_name', 'get_branches', 'role', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('email', 'full_name', 'phone_number')

    fieldsets = (
        ('Basic Information', {
            'fields': ('email', 'full_name', 'phone_number', 'username', 'password', 'is_active')
        }),
        ('Branch Management', {
            'fields': ('managed_branches',)
        }),
        ('Permissions', {
            'fields': ('groups', 'user_permissions'),
            'classes': ('collapse',),
        }),
    )

    filter_horizontal = ('managed_branches', 'groups', 'user_permissions')

    def get_branches(self, obj):
        branches = obj.managed_branches.all()
        return ", ".join([b.name for b in branches[:3]]) if branches else "-"

    get_branches.short_description = 'Branches'

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        form.request = request
        return form

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)
            return qs.filter(
                Q(role='branch_admin', managed_branches__in=my_branches) |
                Q(pk=request.user.pk)
            ).distinct()
        return qs

    def get_readonly_fields(self, request, obj=None):
        if obj and obj.pk == request.user.pk:
            return ('role', 'managed_restaurants', 'managed_branches')
        return ()

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

    def has_delete_permission(self, request, obj=None):
        if obj and obj.pk == request.user.pk:
            return False
        return super().has_delete_permission(request, obj)


# =====================================================
# 2. RESTAURANT (Read-only)
# =====================================================
@admin.register(Restaurants, site=custom_restaurant_admin_site)
class RestaurantAdminRestaurantAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'get_branches_count')
    search_fields = ('name', 'email')

    fields = ('name', 'email', 'phone')

    def get_branches_count(self, obj):
        count = obj.branches.count()
        return format_html('<b>{}</b> branches', count)

    get_branches_count.short_description = 'Branches'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            return qs.filter(admins=request.user)
        return qs

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


# =====================================================
# 3. BRANCHES
# =====================================================
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
    list_display = ('name', 'restaurant', 'address', 'state', 'status', 'get_categories_count')
    list_filter = ('status', 'state')
    search_fields = ('name', 'address')

    fields = ('name', 'address', 'state', 'status')

    def get_categories_count(self, obj):
        count = obj.food_categories.count()
        return format_html('<b>{}</b> categories', count)

    get_categories_count.short_description = 'Categories'

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
                my_restaurants = get_my_restaurants(request)
                if my_restaurants.exists():
                    obj.restaurant = my_restaurants.first()
        super().save_model(request, obj, form, change)


# =====================================================
# 4. FOOD CATEGORIES
# =====================================================
@admin.register(FoodCategory, site=custom_restaurant_admin_site)
class RestaurantAdminFoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'get_foods_count', 'created_at')
    list_filter = ('branch',)
    search_fields = ('name', 'branch__name')

    fields = ('branch', 'name')

    def get_foods_count(self, obj):
        count = obj.foods.count()
        return format_html('<b>{}</b> foods', count)

    get_foods_count.short_description = 'Foods'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)
            return qs.filter(branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "branch" and request.user.role == 'restaurant_admin':
            kwargs["queryset"] = get_my_branches(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# =====================================================
# 5. FOODS
# =====================================================
@admin.register(Food, site=custom_restaurant_admin_site)
class RestaurantAdminFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_branch', 'price', 'get_discount_info', 'get_image_preview')
    list_filter = ('category__branch', 'category', 'discount_active')
    search_fields = ('name', 'description')

    fieldsets = (
        ('Basic Information', {
            'fields': ('category', 'name', 'description', 'image')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_active', 'discount_percent')
        }),
    )

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

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)
            return qs.filter(category__branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "category" and request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)
            kwargs["queryset"] = FoodCategory.objects.filter(branch__in=my_branches)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# =====================================================
# 6. MENU COLLECTIONS
# =====================================================
@admin.register(FoodMenuBranchCollection, site=custom_restaurant_admin_site)
class RestaurantAdminMenuCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'is_active', 'get_foods_count', 'created_at')
    list_filter = ('is_active', 'branch')
    search_fields = ('name', 'description')

    fields = ('branch', 'name', 'description', 'is_active')

    def get_foods_count(self, obj):
        count = obj.food_items.count()
        return format_html('<b>{}</b> foods', count)

    get_foods_count.short_description = 'Foods'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)
            return qs.filter(branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "branch" and request.user.role == 'restaurant_admin':
            kwargs["queryset"] = get_my_branches(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# =====================================================
# 7. FOOD MENU BRANCH
# =====================================================
@admin.register(FoodMenuBranch, site=custom_restaurant_admin_site)
class RestaurantAdminFoodMenuBranchAdmin(admin.ModelAdmin):
    list_display = ('food', 'collection', 'get_branch', 'is_available', 'added_at')
    list_filter = ('is_available', 'collection__branch', 'collection')
    search_fields = ('food__name', 'collection__name')

    fields = ('collection', 'food', 'is_available')

    def get_branch(self, obj):
        return obj.collection.branch.name

    get_branch.short_description = 'Branch'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)
            return qs.filter(collection__branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if request.user.role == 'restaurant_admin':
            my_branches = get_my_branches(request)

            if db_field.name == "collection":
                kwargs["queryset"] = FoodMenuBranchCollection.objects.filter(branch__in=my_branches)

            elif db_field.name == "food":
                kwargs["queryset"] = Food.objects.filter(category__branch__in=my_branches)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)