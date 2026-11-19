from django.contrib import admin
from django.utils.html import format_html
from .models import Prestamo, Devolucion


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    list_display = (
        "id", "docente", "equipo", "cantidad",
        "fecha_prestamo", "fecha_devolucion",
        "estado_badge", "dias_retraso_col",
    )
    list_filter = ("estado", "fecha_prestamo", "fecha_devolucion", "equipo__laboratorio")
    search_fields = (
        "equipo__codigo_patrimonial", "equipo__nombre",
        "docente__first_name", "docente__last_name", "docente__username",
    )
    autocomplete_fields = ("equipo", "docente")
    list_per_page = 20
    actions = ["recordatorio_devolucion"]

    def get_queryset(self, request):
        # Optimización (N+1)
        return super().get_queryset(request).select_related("equipo", "docente")

    @admin.display(description="Estado")
    def estado_badge(self, obj):
        _, color, label = obj.estado_visual
        hexcolor = {
            "emerald": "#10B981", "blue": "#3B82F6", "rose": "#EF4444",
        }.get(color, "#64748B")
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:999px;font-size:11px;font-weight:600;">{}</span>',
            hexcolor, label,
        )

    @admin.display(description="Días de retraso")
    def dias_retraso_col(self, obj):
        d = obj.dias_retraso
        if d == 0:
            return "—"
        return format_html('<strong style="color:#EF4444;">{} días</strong>', d)

    @admin.action(description="📧 Enviar recordatorio de devolución")
    def recordatorio_devolucion(self, request, queryset):
        n = 0
        for p in queryset.filter(estado="activo"):
            # Simulación de envío de correo
            n += 1
        self.message_user(request, f"Recordatorios enviados a {n} préstamo(s).")


@admin.register(Devolucion)
class DevolucionAdmin(admin.ModelAdmin):
    list_display = ("prestamo", "fecha_devolucion", "estado_equipo", "registrado_por")
    list_filter = ("estado_equipo",)
    readonly_fields = ("fecha_devolucion",)