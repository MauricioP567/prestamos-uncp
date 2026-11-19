from django.db import models
from django.urls import reverse
from django.utils import timezone


class Laboratorio(models.Model):
    nombre = models.CharField(max_length=80, unique=True)
    ubicacion = models.CharField(max_length=120)
    capacidad = models.PositiveIntegerField(default=30)

    class Meta:
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Equipo(models.Model):
    class Estado(models.TextChoices):
        OPERATIVO = "operativo", "Operativo"
        MANTENIMIENTO = "mantenimiento", "En mantenimiento"
        BAJA = "baja", "Dado de baja"

    codigo_patrimonial = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=120)
    marca = models.CharField(max_length=80)
    modelo = models.CharField(max_length=80)
    categoria = models.CharField(max_length=60)
    estado = models.CharField(max_length=20, choices=Estado.choices, default=Estado.OPERATIVO)
    laboratorio = models.ForeignKey(Laboratorio, on_delete=models.PROTECT, related_name="equipos")
    ultimo_mantenimiento = models.DateField(null=True, blank=True)
    stock_total = models.PositiveIntegerField(default=1)
    descripcion = models.TextField(blank=True)
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["nombre"]
        verbose_name = "Equipo"
        verbose_name_plural = "Equipos"

    def __str__(self):
        return f"{self.codigo_patrimonial} — {self.nombre}"

    def get_absolute_url(self):
        return reverse("equipos:detalle", args=[self.pk])

    # Campos calculados
    @property
    def dias_desde_mantenimiento(self):
        if not self.ultimo_mantenimiento:
            return None
        return (timezone.now().date() - self.ultimo_mantenimiento).days

    @property
    def stock_disponible(self):
        activos = self.prestamos.filter(estado="activo").aggregate(
            total=models.Sum("cantidad")
        )["total"] or 0
        return self.stock_total - activos

    @property
    def estado_color(self):
        return {
            "operativo": "emerald",
            "mantenimiento": "amber",
            "baja": "rose",
        }.get(self.estado, "slate")

    @property
    def disponible(self):
        return self.estado == self.Estado.OPERATIVO and self.stock_disponible > 0