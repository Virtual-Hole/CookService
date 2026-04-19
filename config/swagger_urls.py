from django.urls import path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView

from config.views import CustomSwaggerView


swagger_urls = [
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", CustomSwaggerView.as_view(), name="swagger-ui"),
    path("redoc/", SpectacularRedocView.as_view(), name="redoc"),
]
