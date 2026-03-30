from datetime import date

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import get_object_or_404, render

from apps.prestamos.models import Prestamo
from .models import Libro


@login_required
def lista_libros(request):
    q = request.GET.get("q", "").strip()
    libros = Libro.objects.prefetch_related("autores", "categorias").order_by("titulo")
    if q:
        libros = libros.filter(
            Q(titulo__icontains=q)
            | Q(isbn__icontains=q)
            | Q(autores__nombre__icontains=q)
            | Q(autores__apellido__icontains=q)
            | Q(categorias__nombre__icontains=q)
        ).distinct()
    return render(request, "libros/lista.html", {"libros": libros, "q": q})


@login_required
def detalle_libro(request, pk):
    libro = get_object_or_404(
        Libro.objects.prefetch_related("autores", "categorias"), pk=pk
    )

    # Auto-actualizar préstamos vencidos de este libro
    Prestamo.objects.filter(
        libro=libro,
        estado=Prestamo.ESTADO_ACTIVO,
        fecha_devolucion_esperada__lt=date.today(),
    ).update(estado=Prestamo.ESTADO_VENCIDO)

    en_poder = (
        Prestamo.objects.filter(
            libro=libro,
            estado__in=[Prestamo.ESTADO_ACTIVO, Prestamo.ESTADO_VENCIDO],
        )
        .select_related("alumno")
        .order_by("fecha_devolucion_esperada")
    )

    historial = (
        Prestamo.objects.filter(libro=libro, estado=Prestamo.ESTADO_DEVUELTO)
        .select_related("alumno")
        .order_by("-fecha_devolucion_real")[:20]
    )

    return render(request, "libros/detalle.html", {
        "libro": libro,
        "en_poder": en_poder,
        "historial": historial,
        "hoy": date.today(),
    })


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/libros/views.py
# =============================================================================
# Vistas del módulo de libros. Requieren login (@login_required).
#
# FUNCIONES:
#   lista_libros(request)
#       → Muestra todos los libros con prefetch de autores y categorías.
#       → BÚSQUEDA: parámetro GET "q" filtra por título, ISBN, nombre/apellido
#         de autor o nombre de categoría usando OR con Q objects.
#         Template: libros/lista.html
#
#   detalle_libro(request, pk)
#       → Muestra información completa de un libro específico.
#       → Auto-actualiza préstamos vencidos de ese libro antes de mostrar.
#       → CONSULTAS:
#           en_poder  → préstamos ACTIVO o VENCIDO del libro (quién lo tiene).
#           historial → últimas 20 devoluciones del libro.
#         Template: libros/detalle.html
# =============================================================================
