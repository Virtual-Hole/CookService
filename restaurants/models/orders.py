import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models

from .restaurant_branches import RestaurantBranches
from .restaurants import Restaurants


class Order(models.Model):
    class StatusChoices(models.TextChoices):
        PENDING = "pending", "pending"
        ACCEPTED = "accepted", "accepted"
        ON_THE_WAY = "on_the_way", "on_the_way"
        DELIVERED = "delivered", "delivered"
        CANCELLED = "cancelled", "cancelled"

    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    customer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="customer_orders",
    )
    courier = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="courier_orders",
    )
    restaurant = models.ForeignKey(
        Restaurants,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    branch = models.ForeignKey(
        RestaurantBranches,
        on_delete=models.CASCADE,
        related_name="orders",
    )
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=StatusChoices.choices,
        default=StatusChoices.PENDING,
    )
    note = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "orders"
        ordering = ["-created_at"]

    def clean(self):
        if self.branch and self.restaurant and self.branch.restaurant_id != self.restaurant_id:
            raise ValidationError({"branch": "Branch must belong to selected restaurant."})

        if self.courier and getattr(self.courier, "role", None) != "courier":
            raise ValidationError({"courier": "Selected courier user role must be courier."})

    def __str__(self):
        return f"{self.uid} - {self.status}"
