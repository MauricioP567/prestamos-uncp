from django.urls import path
from . import views

app_name = "equipos"

urlpatterns = [
    path("", views.catalogo, name="catalogo"),
    path("<int:pk>/", views.detalle, name="detalle"),
]