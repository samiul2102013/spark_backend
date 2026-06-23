from django.core.cache import cache
from django.db import connection
from drf_spectacular.utils import extend_schema, extend_schema_view
from drf_spectacular.views import SpectacularAPIView
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView

from core.responses import success_response


class FilteredSpectacularAPIView(SpectacularAPIView):
    filter_tag = None

    def get(self, request, *args, **kwargs):
        response = super().get(request, *args, **kwargs)
        schema = response.data
        if self.filter_tag and isinstance(schema, dict):
            paths = {}
            for path, methods in schema.get("paths", {}).items():
                filtered = {}
                for method, operation in methods.items():
                    tags = operation.get("tags", [])
                    if tags and self.filter_tag in tags:
                        filtered[method] = operation
                if filtered:
                    paths[path] = filtered
            schema["paths"] = paths
            response.data = schema
        return response


@extend_schema_view(get=extend_schema(request=None, responses={200: None}, tags=["health"]))
class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        db_ok = False
        redis_ok = False
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                db_ok = True
        except Exception:
            db_ok = False
        try:
            cache.set("health_check", "ok", 5)
            redis_ok = cache.get("health_check") == "ok"
        except Exception:
            redis_ok = False
        data = {"db": "ok" if db_ok else "error", "redis": "ok" if redis_ok else "error"}
        http_status = 200 if (db_ok and redis_ok) else 503
        return success_response(data, "Health check", http_status)
