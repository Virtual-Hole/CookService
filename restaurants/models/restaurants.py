from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

phone_regex = RegexValidator(
    regex=r'^\+998\d{9}$',
    message="Phone number must be entered in the format: '+998123456789'. Up to 15 digits allowed."
)

class Restaurants(models.Model):
    name = models.CharField(max_length=255, db_index=True)
    admins = models.ManyToManyField(User, related_name='restaurant_admin', blank=True)
    logo = models.ImageField(upload_to='restaurant_logos/', null=True, blank=True)
    phone = models.CharField(max_length=13, validators=[phone_regex])
    email = models.EmailField(max_length=50, unique=True, null=True, blank=True)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'restaurants'
        verbose_name = 'Restaurant'
        verbose_name_plural = 'Restaurants'
        ordering = ['name']

    def __str__(self):
        return self.name

