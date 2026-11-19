import logging
from .models import LogAuditoria

logger = logging.getLogger("auditoria")


def registrar(usuario, accion, descripcion, request=None):
    ip = None
    ruta = ""
    if request:
        ip = request.META.get("REMOTE_ADDR")
        ruta = request.path
    logger.info("%s | %s | %s", usuario, accion, descripcion)
    return LogAuditoria.objects.create(
        usuario=usuario, accion=accion, descripcion=descripcion, ip=ip, ruta=ruta,
    )