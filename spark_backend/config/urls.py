from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)

from core.views import HealthCheckView

api_prefix = "api/v1/"

urlpatterns = [
    path("admin/", admin.site.urls),
    path(f"{api_prefix}health/", HealthCheckView.as_view(), name="health-check"),
    path(f"{api_prefix}schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        f"{api_prefix}docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    # Mobile
    path(f"{api_prefix}", include("apps.users.urls")),
    path(f"{api_prefix}", include("apps.hubs.urls")),
    path(f"{api_prefix}", include("apps.hazards.urls")),
    path(f"{api_prefix}", include("apps.bookings.urls")),
    path(f"{api_prefix}", include("apps.comms.urls")),
    # Dashboard
    path(f"{api_prefix}", include("apps.dashboard.urls")),
    # Admin
    path(f"{api_prefix}", include("apps.admin_api.urls")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
