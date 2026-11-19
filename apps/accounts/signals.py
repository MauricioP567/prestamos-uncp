from django.db.models.signals import post_migrate
from django.contrib.auth.models import Group, Permission
from django.dispatch import receiver


@receiver(post_migrate)
def crear_grupos_permisos(sender, **kwargs):
    if sender.name != "apps.accounts":
        return
    grupos = {
        "Administrador": ["add", "change", "delete", "view"],
        "Docente": ["view"],
        "Asistente": ["view", "change"],
    }
    for nombre in grupos:
        Group.objects.get_or_create(name=nombre)