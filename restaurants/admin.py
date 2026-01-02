from django.contrib import admin
from restaurants.models import *

# Register your models here.
admin.site.register([Restaurants, RestaurantBranches])