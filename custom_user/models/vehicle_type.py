import uuid
from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models


class VehicleType(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="vehicle_types",
    )
    name = models.CharField(max_length=120)
    min_km = models.PositiveIntegerField()
    max_km = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicle_types"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_vehicle_type_per_user")
        ]

    def clean(self):
        if self.max_km < self.min_km:
            raise ValidationError({"max_km": "max_km must be greater than or equal to min_km."})

        role = getattr(self.user, "role", None)
        if role and role != "courier":
            raise ValidationError({"user": "Vehicle type user must be a courier."})

    def __str__(self):
        return f"{self.user.phone_number} - {self.name}"
