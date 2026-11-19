from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from .models import Usuario


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Usuario UNCP",
        widget=forms.TextInput(attrs={
            "class": "form-input",
            "placeholder": "ej: jlopez",
            "autocomplete": "username",
        }),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(attrs={
            "class": "form-input",
            "placeholder": "••••••••",
            "autocomplete": "current-password",
        }),
    )


class UsuarioCreationForm(UserCreationForm):
    class Meta:
        model = Usuario
        fields = ("username", "first_name", "last_name", "email",
                  "codigo_uncp", "dni", "telefono", "rol")

    def clean_dni(self):
        dni = self.cleaned_data["dni"]
        if not dni.isdigit() or len(dni) != 8:
            raise forms.ValidationError("El DNI debe tener exactamente 8 dígitos numéricos.")
        return dni

    def clean_codigo_uncp(self):
        codigo = self.cleaned_data["codigo_uncp"].upper()
        if not codigo.startswith("U"):
            raise forms.ValidationError("El código UNCP debe iniciar con 'U'.")
        return codigo