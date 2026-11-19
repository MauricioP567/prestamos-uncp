from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Equipo, Laboratorio


def catalogo(request):
    qs = Equipo.objects.select_related("laboratorio").all()
    q = request.GET.get("q", "").strip()
    lab = request.GET.get("lab", "")
    estado = request.GET.get("estado", "")

    if q:
        qs = qs.filter(
            Q(codigo_patrimonial__icontains=q)
            | Q(nombre__icontains=q)
            | Q(categoria__icontains=q)
        )
    if lab:
        qs = qs.filter(laboratorio_id=lab)
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 9)
    page = paginator.get_page(request.GET.get("page"))

    return render(request, "equipos/catalogo.html", {
        "page_obj": page,
        "laboratorios": Laboratorio.objects.all(),
        "q": q, "lab": lab, "estado": estado,
    })


@login_required
def detalle(request, pk):
    equipo = get_object_or_404(
        Equipo.objects.select_related("laboratorio"), pk=pk
    )
    return render(request, "equipos/detalle.html", {"equipo": equipo})