import uuid
from django.contrib.auth.hashers import make_password
from django.db import IntegrityError, models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db.models import Max
from django.utils import timezone

from custom_user.phone import normalize_uz_phone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone_number, password=None, **extra_fields):
        if not phone_number:
            raise ValueError('The phone number must be set')
        user = self.model(phone_number=phone_number, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone_number, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone_number, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    COURIER_ID_START = 835950

    class RoleChoices(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'super_admin'
        RESTAURANT_ADMIN = 'restaurant_admin', 'restaurant_admin'
        BRANCH_ADMIN = 'branch_admin', 'branch_admin'
        COURIER = 'courier', 'courier'
        USER = 'user', 'user'

    uid = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    email = models.EmailField(unique=True, null=True)
    phone_number = models.CharField(max_length=15, null=False, unique=True)
    full_name = models.CharField(max_length=30, null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)
    profile_photo = models.ImageField(
        upload_to="media/profile_photos/",
        default="default_user.png",
        blank=True,
        null=True
    )
    notification = models.BooleanField(default=False)
    promotional_notification = models.BooleanField(default=False)
    role = models.CharField(max_length=50, choices=RoleChoices, default=RoleChoices.SUPER_ADMIN)
    courier_id = models.BigIntegerField(unique=True, null=True, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    managed_restaurants = models.ManyToManyField(
        'restaurants.Restaurants',
        related_name='admins',
        blank=True
    )

    managed_branches = models.ManyToManyField(
        'restaurants.RestaurantBranches',
        related_name='admins',
        blank=True
    )

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = []

    def __str__(self):
        return f"{self.full_name} -> {self.phone_number}"

    def set_password(self, raw_password):
        self.password = make_password(raw_password)

    @classmethod
    def get_next_courier_id(cls):
        max_value = cls.objects.filter(
            role=cls.RoleChoices.COURIER,
            courier_id__isnull=False,
        ).aggregate(max_courier_id=Max("courier_id"))["max_courier_id"]
        return (max_value or cls.COURIER_ID_START) + 1

    def save(self, *args, **kwargs):
        if self.phone_number:
            try:
                self.phone_number = normalize_uz_phone(self.phone_number)
            except ValueError as exc:
                raise ValidationError({"phone_number": str(exc)})

        if self.role == self.RoleChoices.COURIER and not self.courier_id:
            for _ in range(5):
                self.courier_id = self.get_next_courier_id()
                try:
                    return super().save(*args, **kwargs)
                except IntegrityError:
                    self.courier_id = None
            raise IntegrityError("Could not generate unique courier_id.")

        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"
