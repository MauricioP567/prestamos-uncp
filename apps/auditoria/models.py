from django.conf import settings
from django.db import models


class LogAuditoria(models.Model):
    class Accion(models.TextChoices):
        LOGIN = "login", "Inicio de sesión"
        LOGOUT = "logout", "Cierre de sesión"
        CREAR = "crear", "Creación"
        EDITAR = "editar", "Edición"
        ELIMINAR = "eliminar", "Eliminación"
        PRESTAMO = "prestamo", "Préstamo"
        DEVOLUCION = "devolucion", "Devolución"
        ACCESO_DENEGADO = "acceso_denegado", "Acceso denegado"

    usuario = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name="logs",
    )
    accion = models.CharField(max_length=30, choices=Accion.choices)
    descripcion = models.TextField()
    ip = models.GenericIPAddressField(null=True, blank=True)
    ruta = models.CharField(max_length=255, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-timestamp"]
        verbose_name = "Log de auditoría"
        verbose_name_plural = "Logs de auditoría"

    def __str__(self):
        return f"[{self.timestamp:%d/%m %H:%M}] {self.get_accion_display()} — {self.usuario}"