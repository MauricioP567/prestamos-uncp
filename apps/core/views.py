from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from apps.equipos.models import Equipo
from apps.prestamos.models import Prestamo


def landing(request):
    return render(request, "core/landing.html", {
        "total_equipos": Equipo.objects.count(),
        "total_prestamos": Prestamo.objects.count(),
    })


@login_required
def dashboard(request):
    user = request.user
    prestamos_qs = Prestamo.objects.select_related("equipo", "docente")
    if user.es_docente:
        prestamos_qs = prestamos_qs.filter(docente=user)

    ctx = {
        "total_equipos": Equipo.objects.count(),
        "equipos_operativos": Equipo.objects.filter(estado="operativo").count(),
        "prestamos_activos": prestamos_qs.filter(estado="activo").count(),
        "prestamos_vencidos": sum(1 for p in prestamos_qs if p.esta_vencido),
        "ultimos": prestamos_qs[:5],
    }
    return render(request, "core/dashboard.html", ctx)