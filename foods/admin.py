from django.contrib import admin
from django.utils.html import format_html
from custom_user.models import CustomUser
from restaurants.models import RestaurantBranches
from foods.models import FoodCategory, Food, FoodMenuBranchCollection, FoodMenuBranch


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


# =====================================================
# HELPER: O'z branch'larini olish
# =====================================================
def get_my_branches(request):
    """Request user'ning branch'larini qaytaradi"""
    if request.user.role == 'branch_admin':
        return request.user.managed_branches.all()
    return RestaurantBranches.objects.none()


# =====================================================
# 1. USER PROFILE (O'zini ko'rish va tahrirlash)
# =====================================================
@admin.register(CustomUser, site=custom_branch_admin_site)
class BranchAdminUserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'get_branches', 'is_active')

    fields = ('email', 'full_name', 'phone_number', 'password', 'is_active')
    readonly_fields = ('email',)  # Email o'zgartirib bo'lmaydi

    def get_branches(self, obj):
        branches = obj.managed_branches.all()
        return ", ".join([b.name for b in branches]) if branches else "-"

    get_branches.short_description = 'My Branches'

    def get_queryset(self, request):
        """Faqat o'zini ko'rsatish"""
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            return qs.filter(pk=request.user.pk)
        return qs

    def has_add_permission(self, request):
        """Yangi user qo'sha olmaydi"""
        return False

    def has_delete_permission(self, request, obj=None):
        """O'zini o'chira olmaydi"""
        return False

    def save_model(self, request, obj, form, change):
        """Faqat parol va basic info o'zgartirish"""
        if 'password' in form.changed_data:
            obj.set_password(obj.password)
        super().save_model(request, obj, form, change)


# =====================================================
# 2. BRANCHES (Read-only)
# =====================================================
@admin.register(RestaurantBranches, site=custom_branch_admin_site)
class BranchAdminBranchesAdmin(admin.ModelAdmin):
    list_display = ('name', 'restaurant', 'address', 'state', 'status')

    fields = ('restaurant', 'name', 'address', 'state', 'status')
    readonly_fields = ('restaurant', 'name', 'address', 'state', 'status')

    def get_queryset(self, request):
        """Faqat o'z branch'larini ko'rsatish"""
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            return qs.filter(admins=request.user)
        return qs

    def has_add_permission(self, request):
        """Yangi branch qo'sha olmaydi"""
        return False

    def has_delete_permission(self, request, obj=None):
        """Branch o'chira olmaydi"""
        return False

    def has_change_permission(self, request, obj=None):
        """Branch o'zgartira olmaydi (faqat ko'radi)"""
        return False


# =====================================================
# 4. FOODS (Full CRUD)
# =====================================================
@admin.register(Food, site=custom_branch_admin_site)
class BranchAdminFoodAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'get_branch', 'price', 'get_discount_info', 'get_image_preview', 'created_at')
    list_filter = ('category', 'discount_active')
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
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 5px;" />',
                obj.image.url
            )
        return '-'

    get_image_preview.short_description = 'Image'

    def get_queryset(self, request):
        """Faqat o'z branch'laridagi foodlarni ko'rsatish"""
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return qs.filter(category__branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Faqat o'z branch'larining kategoriyalarini ko'rsatish"""
        if db_field.name == "category" and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            kwargs["queryset"] = FoodCategory.objects.filter(branch__in=my_branches)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        """Faqat o'z branch'idagi foodlarni tahrirlash"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.category.branch in my_branches
        return True

    def has_delete_permission(self, request, obj=None):
        """Faqat o'z branch'idagi foodlarni o'chirish"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.category.branch in my_branches
        return True


# restaurants/branch_admin.py

# =====================================================
# 3. FOOD CATEGORIES (Full CRUD) ✅
# =====================================================
@admin.register(FoodCategory, site=custom_branch_admin_site)
class BranchAdminFoodCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'get_foods_count', 'created_at')
    list_filter = ('branch',)
    search_fields = ('name',)

    fields = ('branch', 'name')

    def get_foods_count(self, obj):
        count = obj.foods.count()
        return format_html('<b>{}</b> foods', count)

    get_foods_count.short_description = 'Foods'

    def get_queryset(self, request):
        """Faqat o'z branch'larining kategoriyalarini ko'rsatish"""
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return qs.filter(branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Faqat o'z branch'larini ko'rsatish"""
        if db_field.name == "branch" and request.user.role == 'branch_admin':
            kwargs["queryset"] = get_my_branches(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        """Faqat o'z branch'idagi kategoriyalarni tahrirlash"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.branch in my_branches
        return True

    def has_delete_permission(self, request, obj=None):
        """Faqat o'z branch'idagi kategoriyalarni o'chirish"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.branch in my_branches
        return True


# =====================================================
# 5. MENU COLLECTIONS (Full CRUD) ✅
# =====================================================
@admin.register(FoodMenuBranchCollection, site=custom_branch_admin_site)
class BranchAdminMenuCollectionAdmin(admin.ModelAdmin):
    list_display = ('name', 'branch', 'is_active', 'get_foods_count', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('name', 'description')

    fields = ('branch', 'name', 'description', 'is_active')

    def get_foods_count(self, obj):
        count = obj.food_items.count()
        return format_html('<b>{}</b> foods', count)

    get_foods_count.short_description = 'Foods in Menu'

    def get_queryset(self, request):
        """Faqat o'z branch'larining kolleksiyalarini ko'rsatish"""
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return qs.filter(branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Faqat o'z branch'larini ko'rsatish"""
        if db_field.name == "branch" and request.user.role == 'branch_admin':
            kwargs["queryset"] = get_my_branches(request)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        """Faqat o'z branch'idagi kolleksiyalarni tahrirlash"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.branch in my_branches
        return True

    def has_delete_permission(self, request, obj=None):
        """Faqat o'z branch'idagi kolleksiyalarni o'chirish"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.branch in my_branches
        return True


# =====================================================
# 6. FOOD MENU BRANCH (Full CRUD)
# =====================================================
@admin.register(FoodMenuBranch, site=custom_branch_admin_site)
class BranchAdminFoodMenuBranchAdmin(admin.ModelAdmin):
    list_display = ('food', 'collection', 'get_branch', 'is_available', 'added_at')
    list_filter = ('is_available', 'collection')
    search_fields = ('food__name', 'collection__name')

    fields = ('collection', 'food', 'is_available')

    def get_branch(self, obj):
        return obj.collection.branch.name

    get_branch.short_description = 'Branch'

    def get_queryset(self, request):
        """Faqat o'z branch'laridagi menu itemlarni ko'rsatish"""
        qs = super().get_queryset(request)
        if request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return qs.filter(collection__branch__in=my_branches)
        return qs

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Faqat o'z branch'larining ma'lumotlarini ko'rsatish"""
        if request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)

            if db_field.name == "collection":
                kwargs["queryset"] = FoodMenuBranchCollection.objects.filter(branch__in=my_branches)

            elif db_field.name == "food":
                kwargs["queryset"] = Food.objects.filter(category__branch__in=my_branches)

        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def has_change_permission(self, request, obj=None):
        """Faqat o'z branch'idagi menu itemlarni tahrirlash"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.collection.branch in my_branches
        return True

    def has_delete_permission(self, request, obj=None):
        """Faqat o'z branch'idagi menu itemlarni o'chirish"""
        if obj and request.user.role == 'branch_admin':
            my_branches = get_my_branches(request)
            return obj.collection.branch in my_branches
        return True