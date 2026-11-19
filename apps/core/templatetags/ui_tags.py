from django import template

register = template.Library()

@register.filter
def badge_class(estado):
    return {
        "operativo": "badge-success",
        "activo": "badge-info",
        "mantenimiento": "badge-warning",
        "vencido": "badge-danger",
        "devuelto": "badge-success",
        "baja": "badge-danger",
    }.get(estado, "badge-neutral")