import uuid
from django.db import models
from restaurants.models import RestaurantBranches


class FoodCategory(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    branch = models.ForeignKey(
        RestaurantBranches,
        on_delete=models.CASCADE,
        related_name='food_categories',
        null=True,
        blank=True,
    )
    name = models.CharField(max_length=255)
    logo = models.ImageField(upload_to='food_category_logos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Food Category'
        verbose_name_plural = 'Food Categories'
        unique_together = ['branch', 'name']

    def __str__(self):
        if self.branch_id:
            return f"{self.branch.name} - {self.name}"
        return self.name


class Food(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    image = models.ImageField(upload_to='foods/', blank=True, null=True)
    description = models.TextField()
    category = models.ForeignKey(
        FoodCategory,
        on_delete=models.CASCADE,
        related_name='foods'
    )
    discount_percent = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Chegirma foizi (0-100)"
    )
    discount_active = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Food'
        verbose_name_plural = 'Foods'

    def __str__(self):
        return f"{self.name} ({self.category.name})"

    @property
    def discounted_price(self):
        if self.discount_active and self.discount_percent > 0:
            discount_amount = (self.price * self.discount_percent) / 100
            return self.price - discount_amount
        return self.price

    @property
    def branch(self):
        return self.category.branch if self.category_id else None


class FoodMenuBranchCollection(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    branch = models.ForeignKey(
        RestaurantBranches,
        on_delete=models.CASCADE,
        related_name='menu_collections'
    )
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Food Menu Collection'
        verbose_name_plural = 'Food Menu Collections'
        unique_together = ['branch', 'name']

    def __str__(self):
        return f"{self.branch.name} - {self.name}"


class FoodMenuBranch(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    food = models.ForeignKey(
        Food,
        on_delete=models.CASCADE,
        related_name='menu_branches'
    )
    collection = models.ForeignKey(
        FoodMenuBranchCollection,
        on_delete=models.CASCADE,
        related_name='food_items'
    )

    is_available = models.BooleanField(default=True)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Food Menu Branch'
        verbose_name_plural = 'Food Menu Branches'
        unique_together = ['food', 'collection']

    def __str__(self):
        return f"{self.food.name} in {self.collection.name}"
