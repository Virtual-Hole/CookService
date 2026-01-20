from django.contrib.auth.hashers import make_password
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The email must be set')
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    class RoleChoices(models.TextChoices):
        SUPER_ADMIN = 'super_admin', 'super_admin'
        RESTAURANT_ADMIN = 'restaurant_admin', 'restaurant_admin'
        BRANCH_ADMIN = 'branch_admin', 'branch_admin'
        USER = 'user', 'user'

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

    class Meta:
        verbose_name = "Admin"
        verbose_name_plural = "Admins"


