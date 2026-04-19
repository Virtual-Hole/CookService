from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include

from custom_user.admin import custom_super_admin_site
from restaurants.admin import custom_restaurant_admin_site
from foods.admin import custom_branch_admin_site
from .swagger_urls import swagger_urls


urlpatterns = [
    path('super_admin/', custom_super_admin_site.urls),
    path('restaurant_admin/', custom_restaurant_admin_site.urls),
    path('branch_admin/', custom_branch_admin_site.urls),

    path('api/auth/', include('djoser.urls.jwt')),
    path('api/user/', include('custom_user.urls')),
    path('api/foods/', include('foods.urls')),
    path('api/admin/', include('admin_api.urls')),
]

urlpatterns += swagger_urls

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
