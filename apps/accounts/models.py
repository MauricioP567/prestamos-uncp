from django.contrib.auth.models import AbstractUser
from django.db import models


class Usuario(AbstractUser):
    class Rol(models.TextChoices):
        ADMIN = "admin", "Administrador"
        DOCENTE = "docente", "Docente"
        ASISTENTE = "asistente", "Asistente"
        INVITADO = "invitado", "Invitado"

    rol = models.CharField(
        max_length=20, choices=Rol.choices, default=Rol.INVITADO,
        help_text="Rol que determina los permisos del usuario.",
    )
    codigo_uncp = models.CharField("código UNCP", max_length=15, unique=True)
    dni = models.CharField(max_length=8, unique=True)
    telefono = models.CharField(max_length=15, blank=True)
    avatar_color = models.CharField(max_length=7, default="#3B82F6")

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"

    @property
    def es_admin(self):
        return self.rol == self.Rol.ADMIN or self.is_superuser

    @property
    def es_asistente(self):
        return self.rol == self.Rol.ASISTENTE

    @property
    def es_docente(self):
        return self.rol == self.Rol.DOCENTE

    @property
    def iniciales(self):
        return f"{self.first_name[:1]}{self.last_name[:1]}".upper()

    def save(self, *args, **kwargs):
        # sincroniza rol con grupos de Django (para permisos nativos)
        super().save(*args, **kwargs)
        from django.contrib.auth.models import Group
        grupo, _ = Group.objects.get_or_create(name=self.get_rol_display())
        self.groups.set([grupo])