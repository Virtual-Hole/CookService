from django.contrib import admin
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken, BlacklistedToken
from rest_framework_simplejwt.token_blacklist.admin import OutstandingTokenAdmin, BlacklistedTokenAdmin

from custom_user.models import *

admin.site.register([CustomUser, Card, Address, Device])

admin.site.unregister(OutstandingToken)
admin.site.unregister(BlacklistedToken)