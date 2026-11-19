from apps.prestamos.models import Prestamo


def notificaciones(request):
    if not request.user.is_authenticated:
        return {}
    qs = Prestamo.objects.filter(docente=request.user, estado="activo")
    vencidos = [p for p in qs if p.esta_vencido]
    return {
        "nav_vencidos": len(vencidos),
        "nav_activos": qs.count(),
    }