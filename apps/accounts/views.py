from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.contrib import messages
from .forms import LoginForm


class CustomLoginView(LoginView):
    template_name = "accounts/login.html"
    form_class = LoginForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(
            self.request,
            f"¡Bienvenido de vuelta, {self.request.user.first_name or self.request.user.username}!",
        )
        return response

    def get_success_url(self):
        return reverse_lazy("core:dashboard")


def logout_view(request):
    logout(request)
    messages.info(request, "Sesión cerrada correctamente.")
    return redirect("core:landing")


@login_required
def perfil(request):
    return render(request, "accounts/perfil.html", {"usuario": request.user})