import uuid
from django.core.exceptions import ValidationError
from django.db import models


class VehicleType(models.Model):
    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    name = models.CharField(max_length=120)
    min_km = models.PositiveIntegerField()
    max_km = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "vehicle_types"
        ordering = ["name"]

    def clean(self):
        if self.max_km < self.min_km:
            raise ValidationError({"max_km": "max_km must be greater than or equal to min_km."})

    def __str__(self):
        return self.name
