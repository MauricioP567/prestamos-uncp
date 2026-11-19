from django import forms
from .models import Equipo, Laboratorio


class EquipoForm(forms.ModelForm):
    class Meta:
        model = Equipo
        fields = ["codigo_patrimonial", "nombre", "marca", "modelo",
                  "categoria", "estado", "laboratorio", "ultimo_mantenimiento",
                  "stock_total", "descripcion"]
        widgets = {
            "descripcion": forms.Textarea(attrs={"rows": 3}),
            "ultimo_mantenimiento": forms.DateInput(attrs={"type": "date"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault("class", "form-input")

    def clean_stock_total(self):
        stock = self.cleaned_data["stock_total"]
        if stock < 1:
            raise forms.ValidationError("El stock debe ser al menos 1.")
        return stock

    def clean_codigo_patrimonial(self):
        codigo = self.cleaned_data["codigo_patrimonial"].upper().strip()
        if not codigo.startswith("UNCP-"):
            raise forms.ValidationError("El código patrimonial debe iniciar con 'UNCP-'.")
        return codigo