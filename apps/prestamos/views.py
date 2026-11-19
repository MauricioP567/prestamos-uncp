from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.core.paginator import Paginator
from django.db.models import Q
from .models import Prestamo
from .forms import PrestamoForm, DevolucionForm
from .services import registrar_devolucion
from apps.equipos.models import Equipo


@login_required
def lista(request):
    qs = Prestamo.objects.select_related("docente", "equipo").all()

    # Docentes solo ven sus préstamos (RF3)
    if request.user.es_docente:
        qs = qs.filter(docente=request.user)

    q = request.GET.get("q", "").strip()
    estado = request.GET.get("estado", "")
    if q:
        qs = qs.filter(
            Q(equipo__codigo_patrimonial__icontains=q)
            | Q(docente__first_name__icontains=q)
            | Q(docente__last_name__icontains=q)
        )
    if estado:
        qs = qs.filter(estado=estado)

    paginator = Paginator(qs, 10)
    page = paginator.get_page(request.GET.get("page"))
    return render(request, "prestamos/lista.html", {
        "page_obj": page, "q": q, "estado": estado,
    })


@login_required
def solicitar(request):
    if request.method == "POST":
        form = PrestamoForm(request.POST, docente=request.user)
        if form.is_valid():
            prestamo = form.save(commit=False)
            prestamo.docente = request.user
            prestamo.save()
            messages.success(request, "✅ Solicitud de préstamo registrada correctamente.")
            return redirect("prestamos:lista")
        messages.error(request, "Revisa los errores del formulario.")
    else:
        form = PrestamoForm(docente=request.user)

    return render(request, "prestamos/solicitar.html", {
        "form": form,
        "equipos": Equipo.objects.filter(estado=Equipo.Estado.OPERATIVO),
    })


@login_required
@permission_required("prestamos.change_prestamo", raise_exception=True)
def devolver(request, pk):
    prestamo = get_object_or_404(Prestamo, pk=pk, estado=Prestamo.Estado.ACTIVO)
    if request.method == "POST":
        form = DevolucionForm(request.POST)
        if form.is_valid():
            registrar_devolucion(
                prestamo,
                form.cleaned_data["estado_equipo"],
                form.cleaned_data["observaciones"],
                request.user,
            )
            messages.success(request, "📦 Devolución registrada correctamente.")
            return redirect("prestamos:lista")
    else:
        form = DevolucionForm()
    return render(request, "prestamos/devolver.html", {"form": form, "prestamo": prestamo})


@login_required
def detalle(request, pk):
    prestamo = get_object_or_404(
        Prestamo.objects.select_related("docente", "equipo"), pk=pk
    )
    if request.user.es_docente and prestamo.docente_id != request.user.id:
        messages.error(request, "No tienes permiso para ver este préstamo.")
        return redirect("prestamos:lista")
    return render(request, "prestamos/detalle.html", {"prestamo": prestamo})