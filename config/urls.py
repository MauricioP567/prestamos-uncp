from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "UNCP · Gestión de Préstamos"
admin.site.site_title = "UNCP Admin"
admin.site.index_title = "Panel de administración"

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include(("apps.core.urls", "core"), namespace="core")),
    path("cuentas/", include(("apps.accounts.urls", "accounts"), namespace="accounts")),
    path("equipos/", include(("apps.equipos.urls", "equipos"), namespace="equipos")),
    path("prestamos/", include(("apps.prestamos.urls", "prestamos"), namespace="prestamos")),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)