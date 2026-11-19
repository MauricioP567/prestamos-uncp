from django.contrib import admin
from .models import LogAuditoria


@admin.register(LogAuditoria)
class LogAuditoriaAdmin(admin.ModelAdmin):
    list_display = ("timestamp", "usuario", "accion", "ip", "ruta")
    list_filter = ("accion", "timestamp")
    search_fields = ("usuario__username", "descripcion", "ip")
    readonly_fields = [f.name for f in LogAuditoria._meta.fields]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser