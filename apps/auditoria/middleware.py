import logging
from django.utils.deprecation import MiddlewareMixin
from django.utils import timezone

logger = logging.getLogger("auditoria")


class AuditoriaMiddleware(MiddlewareMixin):
    """
    RF4 — Registro de cada acción crítica:
    usuario, fecha/hora, IP y acción realizada.
    """

    ACCIONES_CRITICAS = {
        "/prestamos/solicitar/": "prestamo",
        "/prestamos/": "devolucion",   # incluye devolver/<pk>/
        "/admin/equipos/equipo/": "editar",
    }

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        path = request.path
        accion = None
        for ruta, a in self.ACCIONES_CRITICAS.items():
            if path.startswith(ruta) and request.method == "POST":
                accion = a
                break

        if accion:
            ip = self._get_client_ip(request)
            logger.info(
                "USUARIO=%s | ACCION=%s | IP=%s | RUTA=%s | FECHA=%s",
                request.user.username, accion, ip, path,
                timezone.now().isoformat(),
            )
            # Persistencia en DB
            from .models import LogAuditoria
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=accion,
                descripcion=f"{request.method} {path}",
                ip=ip,
                ruta=path,
            )
        return None

    def process_response(self, request, response):
        # Logging de intentos de acceso no autorizado
        if response.status_code in (403, 401) and request.user.is_authenticated:
            ip = self._get_client_ip(request)
            logger.warning(
                "ACCESO DENEGADO | USUARIO=%s | IP=%s | RUTA=%s | STATUS=%s",
                request.user.username, ip, request.path, response.status_code,
            )
            from .models import LogAuditoria
            LogAuditoria.objects.create(
                usuario=request.user,
                accion=LogAuditoria.Accion.ACCESO_DENEGADO,
                descripcion=f"Intento a {request.path}",
                ip=ip,
                ruta=request.path,
            )
        return response

    @staticmethod
    def _get_client_ip(request):
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR")


class SesionInactividadMiddleware(MiddlewareMixin):
    """
    RNF — Sesión con timeout de 30 minutos de inactividad.
    Complementa SESSION_COOKIE_AGE.
    """

    TIMEOUT_SEGUNDOS = 1800  # 30 min

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        ahora = timezone.now().timestamp()
        ultima = request.session.get("_ultima_actividad")

        if ultima and (ahora - ultima) > self.TIMEOUT_SEGUNDOS:
            from django.contrib.auth import logout
            from django.contrib import messages
            logout(request)
            messages.info(request, "Tu sesión expiró por inactividad.")
            return None

        request.session["_ultima_actividad"] = ahora
        return None