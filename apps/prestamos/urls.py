from django.urls import path
from . import views

app_name = "prestamos"

urlpatterns = [
    path("", views.lista, name="lista"),
    path("solicitar/", views.solicitar, name="solicitar"),
    path("<int:pk>/", views.detalle, name="detalle"),
    path("<int:pk>/devolver/", views.devolver, name="devolver"),
]