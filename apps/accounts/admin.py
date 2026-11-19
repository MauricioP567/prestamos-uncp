from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Usuario


@admin.register(Usuario)
class UsuarioAdmin(UserAdmin):
    list_display = ("username", "get_full_name", "codigo_uncp", "rol", "is_active")
    list_filter = ("rol", "is_active", "is_staff")
    search_fields = ("username", "first_name", "last_name", "codigo_uncp", "dni")
    ordering = ("username",)
    fieldsets = UserAdmin.fieldsets + (
        ("Datos institucionales", {"fields": ("rol", "codigo_uncp", "dni", "telefono")}),
    )