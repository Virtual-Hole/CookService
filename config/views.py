from drf_spectacular.views import SpectacularSwaggerView


class CustomSwaggerView(SpectacularSwaggerView):
    template_name = "swagger/swagger_ui.html"
