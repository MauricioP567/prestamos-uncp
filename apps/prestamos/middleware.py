from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
from .models import Prestamo


class PrestamosVencidosMiddleware(MiddlewareMixin):
    """
    RF4: Al iniciar sesión, si el usuario tiene préstamos vencidos,
    le muestra una alerta. Solo se ejecuta una vez por sesión.
    """

    def process_request(self, request):
        if not request.user.is_authenticated:
            return None

        if request.session.get("_vencidos_mostrado"):
            return None

        vencidos = Prestamo.objects.filter(
            docente=request.user, estado=Prestamo.Estado.ACTIVO
        )
        vencidos = [p for p in vencidos if p.esta_vencido]
        if vencidos:
            messages.warning(
                request,
                f"⚠️ Tienes {len(vencidos)} préstamo(s) vencido(s). "
                "Por favor regulariza la devolución.",
            )
        request.session["_vencidos_mostrado"] = True
        return None