from django.db import models
from django.conf import settings
from django.utils import timezone
from apps.equipos.models import Equipo


class Prestamo(models.Model):
    class Estado(models.TextChoices):
        ACTIVO = "activo", "Activo"
        DEVUELTO = "devuelto", "Devuelto"
        VENCIDO = "vencido", "Vencido"

    docente = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT,
        related_name="prestamos", verbose_name="Docente",
    )
    equipo = models.ForeignKey(
        Equipo, on_delete=models.PROTECT, related_name="prestamos",
    )
    cantidad = models.PositiveIntegerField(default=1)
    fecha_prestamo = models.DateField(default=timezone.localdate)
    fecha_devolucion = models.DateField()
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.ACTIVO)
    observaciones = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"

    def __str__(self):
        return f"#{self.pk} · {self.docente.get_full_name()} → {self.equipo.nombre}"

    @property
    def dias_retraso(self):
        if self.estado == self.Estado.DEVUELTO:
            return 0
        delta = (timezone.localdate() - self.fecha_devolucion).days
        return max(delta, 0)

    @property
    def esta_vencido(self):
        return self.estado == self.Estado.ACTIVO and timezone.localdate() > self.fecha_devolucion

    @property
    def estado_visual(self):
        if self.estado == self.Estado.DEVUELTO:
            return ("devuelto", "emerald", "Devuelto")
        if self.esta_vencido:
            return ("vencido", "rose", f"Vencido ({self.dias_retraso}d)")
        return ("activo", "blue", "Activo")

    def save(self, *args, **kwargs):
        if self.esta_vencido:
            self.estado = self.Estado.VENCIDO
        super().save(*args, **kwargs)


class Devolucion(models.Model):
    prestamo = models.OneToOneField(
        Prestamo, on_delete=models.CASCADE, related_name="devolucion",
    )
    fecha_devolucion = models.DateTimeField(auto_now_add=True)
    estado_equipo = models.CharField(
        max_length=20, choices=Equipo.Estado.choices, default=Equipo.Estado.OPERATIVO,
    )
    observaciones = models.TextField(blank=True)
    registrado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True,
    )

    def __str__(self):
        return f"Devolución de préstamo #{self.prestamo_id}"