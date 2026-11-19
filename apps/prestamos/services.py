from django.db import transaction
from django.utils import timezone
from .models import Prestamo, Devolucion


@transaction.atomic
def registrar_devolucion(prestamo: Prestamo, estado_equipo: str, obs: str, usuario):
    dev = Devolucion.objects.create(
        prestamo=prestamo,
        estado_equipo=estado_equipo,
        observaciones=obs,
        registrado_por=usuario,
    )
    prestamo.estado = Prestamo.Estado.DEVUELTO
    prestamo.save()
    # Sincroniza estado del equipo
    equipo = prestamo.equipo
    equipo.estado = estado_equipo
    equipo.save(update_fields=["estado"])
    return dev