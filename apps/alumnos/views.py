from datetime import date

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Q
from django.shortcuts import get_object_or_404, redirect, render

from apps.multas.models import Multa
from apps.prestamos.models import Prestamo
from .models import Alumno


@login_required
def lista_alumnos(request):
    q = request.GET.get("q", "").strip()
    alumnos = Alumno.objects.annotate(
        prestamos_activos=Count(
            "prestamos",
            filter=Q(prestamos__estado__in=[Prestamo.ESTADO_ACTIVO, Prestamo.ESTADO_VENCIDO]),
        )
    ).order_by("apellido", "nombre")
    if q:
        alumnos = alumnos.filter(
            Q(nombre__icontains=q) | Q(apellido__icontains=q) | Q(carnet__icontains=q)
        )
    return render(request, "alumnos/lista.html", {"alumnos": alumnos, "q": q})


@login_required
def perfil_alumno(request, pk):
    alumno = get_object_or_404(Alumno, pk=pk)

    # Auto-actualizar vencidos de este alumno
    Prestamo.objects.filter(
        alumno=alumno,
        estado=Prestamo.ESTADO_ACTIVO,
        fecha_devolucion_esperada__lt=date.today(),
    ).update(estado=Prestamo.ESTADO_VENCIDO)

    prestamos_activos = (
        Prestamo.objects.filter(
            alumno=alumno,
            estado__in=[Prestamo.ESTADO_ACTIVO, Prestamo.ESTADO_VENCIDO],
        )
        .select_related("libro")
        .order_by("fecha_devolucion_esperada")
    )

    multas_pendientes = (
        Multa.objects.filter(
            prestamo__alumno=alumno,
            estado=Multa.ESTADO_PENDIENTE,
        )
        .select_related("prestamo__libro")
    )

    historial = (
        Prestamo.objects.filter(alumno=alumno, estado=Prestamo.ESTADO_DEVUELTO)
        .select_related("libro")
        .order_by("-fecha_devolucion_real")[:15]
    )

    return render(request, "alumnos/perfil.html", {
        "alumno": alumno,
        "prestamos_activos": prestamos_activos,
        "multas_pendientes": multas_pendientes,
        "historial": historial,
        "hoy": date.today(),
    })


@login_required
def devolver_libro(request, pk, prestamo_id):
    if request.method != "POST":
        return redirect("perfil_alumno", pk=pk)

    prestamo = get_object_or_404(Prestamo, pk=prestamo_id, alumno__pk=pk)

    if prestamo.estado != Prestamo.ESTADO_DEVUELTO:
        prestamo.fecha_devolucion_real = date.today()
        prestamo.save()  
        # save() + signal manejan disponibilidad y multa

        multa = Multa.objects.filter(prestamo=prestamo).first()
        if multa:
            messages.warning(
                request,
                f'"{prestamo.libro}" devuelto tarde. Multa generada: ${multa.monto}.',
            )
        else:
            messages.success(request, f'"{prestamo.libro}" devuelto correctamente.')

    return redirect("perfil_alumno", pk=pk)


@login_required
def pagar_multa(request, pk, multa_id):
    if request.method != "POST":
        return redirect("perfil_alumno", pk=pk)

    multa = get_object_or_404(Multa, pk=multa_id, prestamo__alumno__pk=pk)

    if multa.estado == Multa.ESTADO_PENDIENTE:
        multa.estado = Multa.ESTADO_PAGADA
        multa.fecha_pago = date.today()
        multa.save()
        messages.success(request, f"Multa de ${multa.monto} marcada como pagada.")

    return redirect("perfil_alumno", pk=pk)


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/alumnos/views.py
# =============================================================================
# Vistas del módulo de alumnos. Todas requieren login (@login_required).
#
# FUNCIONES:
#   lista_alumnos(request)
#       → Lista todos los alumnos ordenados por apellido.
#       → Usa annotate() para contar préstamos activos+vencidos de cada alumno
#         sin hacer queries adicionales en el template.
#       → BÚSQUEDA: parámetro GET "q" filtra por nombre, apellido o carnet.
#         Template: alumnos/lista.html
#
#   perfil_alumno(request, pk)
#       → Perfil completo de un alumno.
#       → Auto-actualiza vencidos del alumno antes de mostrar.
#       → CONSULTAS:
#           prestamos_activos  → préstamos ACTIVO o VENCIDO del alumno.
#           multas_pendientes  → multas sin pagar del alumno.
#           historial          → últimas 15 devoluciones.
#         Template: alumnos/perfil.html
#
#   devolver_libro(request, pk, prestamo_id)
#       → Solo acepta POST. Registra fecha_devolucion_real = hoy.
#       → El método save() y los signals manejan: cambio de estado, incremento
#         de disponibilidad y generación automática de multa si aplica.
#       → Muestra mensaje de advertencia si se generó multa, éxito si no.
#
#   pagar_multa(request, pk, multa_id)
#       → Solo acepta POST. Marca la multa como PAGADA y registra fecha_pago.
#       → Solo actúa si la multa está en estado PENDIENTE.
# =============================================================================
