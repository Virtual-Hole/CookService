from django.conf import settings
from django.conf.urls.static import static
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView

from custom_user.admin import custom_super_admin_site
from restaurants.admin import custom_restaurant_admin_site
from foods.admin import custom_branch_admin_site


urlpatterns = [
    path('super_admin/', custom_super_admin_site.urls),
    path('restaurant_admin/', custom_restaurant_admin_site.urls),
    path('branch_admin/', custom_branch_admin_site.urls),

    path('api/auth/', include('djoser.urls.jwt')),
    path('api/user/', include('custom_user.urls')),
    path('api/foods/', include('foods.urls')),
    path('api/admin/', include('admin_api.urls')),

    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
