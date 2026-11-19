from django import forms
from django.utils import timezone
from django.utils.html import strip_tags
from django.core.exceptions import ValidationError
from .models import Prestamo, Devolucion
from apps.equipos.models import Equipo


class PrestamoForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = ["equipo", "cantidad", "fecha_prestamo", "fecha_devolucion", "observaciones"]
        widgets = {
            "fecha_prestamo": forms.DateInput(attrs={"type": "date"}),
            "fecha_devolucion": forms.DateInput(attrs={"type": "date"}),
            "observaciones": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, docente=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.docente = docente
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-input")

        # Solo equipos operativos y con stock disponible
        self.fields["equipo"].queryset = (
            Equipo.objects.filter(estado=Equipo.Estado.OPERATIVO)
            .select_related("laboratorio")
        )
        self.fields["equipo"].empty_label = "Seleccione un equipo..."

    # -- Validaciones por campo --
    def clean_fecha_prestamo(self):
        fecha = self.cleaned_data["fecha_prestamo"]
        if fecha < timezone.localdate():
            raise ValidationError("La fecha de préstamo no puede ser anterior a hoy.")
        return fecha

    def clean_cantidad(self):
        cantidad = self.cleaned_data["cantidad"]
        if cantidad < 1:
            raise ValidationError("La cantidad debe ser al menos 1.")
        return cantidad

    def clean_observaciones(self):
        # sanitización básica (equivalente a bleach para este alcance)
        texto = strip_tags(self.cleaned_data.get("observaciones", ""))
        return texto.strip()

    # -- Validación cruzada --
    def clean(self):
        cleaned = super().clean()
        equipo = cleaned.get("equipo")
        cantidad = cleaned.get("cantidad")
        f_ini = cleaned.get("fecha_prestamo")
        f_fin = cleaned.get("fecha_devolucion")

        # 1) Fecha fin > fecha inicio
        if f_ini and f_fin and f_fin <= f_ini:
            self.add_error("fecha_devolucion",
                           "La fecha de devolución debe ser posterior a la de préstamo.")

        # 2) Docente no puede tener más de 3 préstamos activos
        if self.docente:
            activos = Prestamo.objects.filter(
                docente=self.docente, estado=Prestamo.Estado.ACTIVO
            ).exclude(pk=self.instance.pk).count()
            if activos >= 3:
                raise ValidationError(
                    "No puede solicitar más de 3 préstamos activos simultáneamente."
                )

        # 3) Equipo operativo y con stock suficiente
        if equipo and cantidad:
            if equipo.estado != Equipo.Estado.OPERATIVO:
                self.add_error("equipo", "El equipo no está operativo.")
            elif cantidad > equipo.stock_disponible:
                self.add_error(
                    "cantidad",
                    f"Stock insuficiente. Disponible: {equipo.stock_disponible}."
                )
        return cleaned


class DevolucionForm(forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ["estado_equipo", "observaciones"]
        widgets = {"observaciones": forms.Textarea(attrs={"rows": 3})}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for f in self.fields.values():
            f.widget.attrs.setdefault("class", "form-input")

    def clean_observaciones(self):
        texto = strip_tags(self.cleaned_data.get("observaciones", ""))
        if len(texto.strip()) < 10:
            raise ValidationError("Describa el estado del equipo (mínimo 10 caracteres).")
        return texto