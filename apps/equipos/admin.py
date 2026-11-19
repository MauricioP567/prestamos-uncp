from django.contrib import admin
from django.utils.html import format_html
from .models import Equipo, Laboratorio


@admin.register(Laboratorio)
class LaboratorioAdmin(admin.ModelAdmin):
    list_display = ("nombre", "ubicacion", "capacidad", "total_equipos")
    search_fields = ("nombre", "ubicacion")

    def total_equipos(self, obj):
        return obj.equipos.count()
    total_equipos.short_description = "Equipos"


@admin.register(Equipo)
class EquipoAdmin(admin.ModelAdmin):
    list_display = (
        "codigo_patrimonial", "nombre", "categoria", "laboratorio",
        "estado_badge", "dias_mant", "stock_disponible",
    )
    list_filter = ("laboratorio", "estado", "categoria")
    search_fields = ("codigo_patrimonial", "nombre", "categoria", "marca")
    list_per_page = 20
    readonly_fields = ("creado",)
    actions = ["marcar_mantenimiento", "marcar_operativo"]

    @admin.display(description="Estado")
    def estado_badge(self, obj):
        colores = {
            "operativo": "#10B981", "mantenimiento": "#F59E0B", "baja": "#EF4444",
        }
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;'
            'border-radius:999px;font-size:11px;font-weight:600;">{}</span>',
            colores.get(obj.estado, "#64748B"),
            obj.get_estado_display(),
        )

    @admin.display(description="Días s/mant.")
    def dias_mant(self, obj):
        d = obj.dias_desde_mantenimiento
        return d if d is not None else "—"

    @admin.action(description="🔧 Marcar como en mantenimiento")
    def marcar_mantenimiento(self, request, queryset):
        updated = queryset.update(estado=Equipo.Estado.MANTENIMIENTO)
        self.message_user(request, f"{updated} equipo(s) marcados en mantenimiento.")

    @admin.action(description="✅ Marcar como operativo")
    def marcar_operativo(self, request, queryset):
        updated = queryset.update(estado=Equipo.Estado.OPERATIVO)
        self.message_user(request, f"{updated} equipo(s) marcados operativos.")