from django.urls import path
from . import views

urlpatterns = [
    path("", views.lista_libros, name="lista_libros"),
    path("<int:pk>/", views.detalle_libro, name="detalle_libro"),
]


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/libros/urls.py
# =============================================================================
# Define las rutas del módulo de libros (prefijo "/libros/" desde urls.py principal).
#
#   /libros/        → lista_libros   (catálogo con búsqueda, requiere login)
#   /libros/<pk>/   → detalle_libro  (detalle con historial, requiere login)
# =============================================================================
