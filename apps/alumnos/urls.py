from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_alumnos, name="lista_alumnos"),
    path("<int:pk>/", views.perfil_alumno, name="perfil_alumno"),
    path("<int:pk>/devolver/<int:prestamo_id>/", views.devolver_libro, name="devolver_libro"),
    path("<int:pk>/pagar/<int:multa_id>/", views.pagar_multa, name="pagar_multa"),
]


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/alumnos/urls.py
# =============================================================================
# Define las rutas del módulo de alumnos (prefijo "/alumnos/" desde urls.py principal).
#
#   /alumnos/                         → lista_alumnos   (lista con búsqueda)
#   /alumnos/<pk>/                    → perfil_alumno   (perfil completo)
#   /alumnos/<pk>/devolver/<id>/      → devolver_libro  (acción POST)
#   /alumnos/<pk>/pagar/<id>/         → pagar_multa     (acción POST)
#
# Las acciones devolver y pagar solo responden a POST; un GET las redirige
# al perfil del alumno sin hacer nada.
# =============================================================================
