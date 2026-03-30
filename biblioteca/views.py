import json
from datetime import date, timedelta

from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.db.models import Q
from django.shortcuts import redirect, render

from apps.alumnos.models import Alumno
from apps.libros.models import Categoria, Libro
from apps.multas.models import Multa
from apps.prestamos.models import Prestamo


def home_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    return redirect("login")


def _to_date(val):
    return val.date() if hasattr(val, "date") else val


def _ultimos_6_meses(hoy):
    """Devuelve lista de date(año, mes, 1) para los últimos 6 meses."""
    meses = []
    year, month = hoy.year, hoy.month
    for i in range(5, -1, -1):
        m = month - i
        y = year
        while m <= 0:
            m += 12
            y -= 1
        meses.append(date(y, m, 1))
    return meses


@login_required
def dashboard(request):
    hoy = date.today()
    meses_inicio = _ultimos_6_meses(hoy)
    inicio = meses_inicio[0]
    mes_labels = [m.strftime("%b %Y") for m in meses_inicio]

    # Sincronizar préstamos vencidos
    Prestamo.objects.filter(
        estado=Prestamo.ESTADO_ACTIVO,
        fecha_devolucion_esperada__lt=hoy,
    ).update(estado=Prestamo.ESTADO_VENCIDO)

    # ── Stats cards ──────────────────────────────────────────────────────────
    stats = {
        "total_libros": Libro.objects.count(),
        "total_alumnos": Alumno.objects.count(),
        "prestamos_activos": Prestamo.objects.filter(estado=Prestamo.ESTADO_ACTIVO).count(),
        "prestamos_vencidos": Prestamo.objects.filter(estado=Prestamo.ESTADO_VENCIDO).count(),
        "multas_pendientes": Multa.objects.filter(estado=Multa.ESTADO_PENDIENTE).count(),
        "monto_multas": Multa.objects.filter(
            estado=Multa.ESTADO_PENDIENTE
        ).aggregate(total=Sum("monto"))["total"] or 0,
    }

    # ── Gradient Stacked Area: préstamos vs devoluciones por mes ─────────────
    raw_prest = list(
        Prestamo.objects.filter(fecha_prestamo__gte=inicio)
        .annotate(mes=TruncMonth("fecha_prestamo"))
        .values("mes").annotate(total=Count("id"))
    )
    raw_devol = list(
        Prestamo.objects.filter(
            fecha_devolucion_real__gte=inicio,
            estado=Prestamo.ESTADO_DEVUELTO,
        )
        .annotate(mes=TruncMonth("fecha_devolucion_real"))
        .values("mes").annotate(total=Count("id"))
    )
    prest_dict = {_to_date(p["mes"]): p["total"] for p in raw_prest}
    devol_dict = {_to_date(p["mes"]): p["total"] for p in raw_devol}
    chart_area = {
        "labels": mes_labels,
        "prestamos": [prest_dict.get(m, 0) for m in meses_inicio],
        "devoluciones": [devol_dict.get(m, 0) for m in meses_inicio],
    }

    # ── Stacked Line: préstamos por estado por mes ───────────────────────────
    raw_por_estado = list(
        Prestamo.objects.filter(fecha_prestamo__gte=inicio)
        .annotate(mes=TruncMonth("fecha_prestamo"))
        .values("mes", "estado").annotate(total=Count("id"))
    )
    estado_mes = {
        Prestamo.ESTADO_ACTIVO: {},
        Prestamo.ESTADO_DEVUELTO: {},
        Prestamo.ESTADO_VENCIDO: {},
    }
    for item in raw_por_estado:
        e = item["estado"]
        m = _to_date(item["mes"])
        if e in estado_mes:
            estado_mes[e][m] = item["total"]
    chart_lineas = {
        "labels": mes_labels,
        "activo":   [estado_mes[Prestamo.ESTADO_ACTIVO].get(m, 0) for m in meses_inicio],
        "devuelto": [estado_mes[Prestamo.ESTADO_DEVUELTO].get(m, 0) for m in meses_inicio],
        "vencido":  [estado_mes[Prestamo.ESTADO_VENCIDO].get(m, 0) for m in meses_inicio],
    }

    # ── Pie: estado de préstamos ─────────────────────────────────────────────
    raw_estados = list(Prestamo.objects.values("estado").annotate(total=Count("id")))
    chart_estados = {
        "labels": [e["estado"].capitalize() for e in raw_estados],
        "data":   [e["total"] for e in raw_estados],
    }

    # ── Pie: estado de multas ────────────────────────────────────────────────
    raw_multas_e = list(Multa.objects.values("estado").annotate(total=Count("id")))
    chart_multas = {
        "labels": [m["estado"].capitalize() for m in raw_multas_e],
        "data":   [m["total"] for m in raw_multas_e],
    }

    # ── Bar: ingresos por multas pagadas por mes ─────────────────────────────
    raw_ingresos = list(
        Multa.objects.filter(
            estado=Multa.ESTADO_PAGADA,
            fecha_pago__gte=inicio,
        )
        .annotate(mes=TruncMonth("fecha_pago"))
        .values("mes")
        .annotate(total=Sum("monto"))
        .order_by("mes")
    )
    ingresos_dict = {_to_date(m["mes"]): float(m["total"]) for m in raw_ingresos}
    chart_ingresos = {
        "labels": mes_labels,
        "data":   [ingresos_dict.get(m, 0) for m in meses_inicio],
        "total":  float(Multa.objects.filter(estado=Multa.ESTADO_PAGADA).aggregate(t=Sum("monto"))["t"] or 0),
    }

    # ── Bar: top 5 libros más prestados ─────────────────────────────────────
    raw_libros = list(
        Prestamo.objects.values("libro__titulo")
        .annotate(total=Count("id"))
        .order_by("-total")[:5]
    )
    chart_libros = {
        "labels": [l["libro__titulo"][:40] for l in raw_libros],
        "data":   [l["total"] for l in raw_libros],
    }

    # ── Tablas operativas ────────────────────────────────────────────────────
    vencidos = (
        Prestamo.objects.filter(estado=Prestamo.ESTADO_VENCIDO)
        .select_related("alumno", "libro")
        .order_by("fecha_devolucion_esperada")[:10]
    )
    proximos = (
        Prestamo.objects.filter(
            estado=Prestamo.ESTADO_ACTIVO,
            fecha_devolucion_esperada__gte=hoy,
            fecha_devolucion_esperada__lte=hoy + timedelta(days=3),
        )
        .select_related("alumno", "libro")
        .order_by("fecha_devolucion_esperada")
    )

    context = {
        "stats": stats,
        "chart_area":    json.dumps(chart_area),
        "chart_lineas":  json.dumps(chart_lineas),
        "chart_estados": json.dumps(chart_estados),
        "chart_multas":   json.dumps(chart_multas),
        "chart_ingresos":       json.dumps(chart_ingresos),
        "chart_ingresos_total": chart_ingresos["total"],
        "chart_libros":   json.dumps(chart_libros),
        "vencidos": vencidos,
        "proximos": proximos,
        "hoy": hoy,
    }
    return render(request, "dashboard.html", context)


def catalogo_publico(request):
    q = request.GET.get("q", "").strip()
    categoria_id = request.GET.get("categoria", "").strip()

    libros = Libro.objects.prefetch_related("autores", "categorias").order_by("titulo")

    if q:
        libros = libros.filter(
            Q(titulo__icontains=q)
            | Q(autores__nombre__icontains=q)
            | Q(autores__apellido__icontains=q)
        ).distinct()

    if categoria_id:
        libros = libros.filter(categorias__id=categoria_id)

    categorias = Categoria.objects.all()

    return render(request, "catalogo.html", {
        "libros": libros,
        "categorias": categorias,
        "q": q,
        "categoria_id": categoria_id,
    })


@login_required
def reporte_morosos(request):
    hoy = date.today()

    vencidos = (
        Prestamo.objects.filter(estado=Prestamo.ESTADO_VENCIDO)
        .select_related("alumno", "libro")
        .order_by("alumno__apellido", "alumno__nombre")
    )
    multas = (
        Multa.objects.filter(estado=Multa.ESTADO_PENDIENTE)
        .select_related("prestamo__alumno", "prestamo__libro")
        .order_by("prestamo__alumno__apellido", "prestamo__alumno__nombre")
    )

    total_multas = multas.aggregate(total=Sum("monto"))["total"] or 0

    return render(request, "reporte_morosos.html", {
        "vencidos": vencidos,
        "multas": multas,
        "total_multas": total_multas,
        "hoy": hoy,
    })


@login_required
def busqueda_global(request):
    q = request.GET.get("q", "").strip()
    libros = []
    alumnos = []

    if q:
        libros = (
            Libro.objects.filter(
                Q(titulo__icontains=q)
                | Q(isbn__icontains=q)
                | Q(autores__nombre__icontains=q)
                | Q(autores__apellido__icontains=q)
            )
            .prefetch_related("autores", "categorias")
            .distinct()[:10]
        )
        alumnos = (
            Alumno.objects.filter(
                Q(nombre__icontains=q)
                | Q(apellido__icontains=q)
                | Q(carnet__icontains=q)
                | Q(email__icontains=q)
            )
            .distinct()[:10]
        )

    return render(request, "busqueda.html", {
        "q": q,
        "libros": libros,
        "alumnos": alumnos,
        "total": len(list(libros)) + len(list(alumnos)),
    })


# =============================================================================
# RESUMEN DEL ARCHIVO: biblioteca/views.py
# =============================================================================
# Vistas principales del proyecto (dashboard, catálogo público, búsqueda, reporte).
#
# FUNCIONES AUXILIARES:
#   _to_date(val)          → normaliza datetime a date para compatibilidad en dicts.
#   _ultimos_6_meses(hoy)  → genera lista de 6 fechas (primer día de cada mes)
#                            usadas como eje X en los gráficos del dashboard.
#
# VISTAS:
#   home_view(request)
#       → Redirige a /dashboard/ si está autenticado, a /login/ si no.
#
#   dashboard(request) ← REQUIERE LOGIN
#       → Panel principal con estadísticas y 6 gráficos.
#       → Auto-sincroniza préstamos vencidos al cargar.
#       → CONSULTAS PRINCIPALES:
#           stats         → counts y sumas de libros, alumnos, préstamos y multas.
#           chart_area    → préstamos vs devoluciones por mes (últimos 6 meses).
#           chart_lineas  → préstamos por estado por mes (activo/devuelto/vencido).
#           chart_estados → distribución de estados de todos los préstamos (pie).
#           chart_multas  → distribución de estados de multas (pie).
#           chart_ingresos→ ingresos por multas pagadas por mes (bar).
#           chart_libros  → top 5 libros más prestados (bar).
#           vencidos      → tabla: 10 préstamos vencidos más antiguos.
#           proximos      → tabla: préstamos que vencen en los próximos 3 días.
#       → Los datos de gráficos se serializan como JSON para ECharts en el template.
#
#   catalogo_publico(request)
#       → Catálogo de libros visible sin login.
#       → FILTROS GET: "q" (título o autor), "categoria" (id de Categoria).
#         Usa Q objects con OR para búsqueda combinada.
#
#   reporte_morosos(request) ← REQUIERE LOGIN
#       → Lista préstamos vencidos y multas pendientes ordenados por alumno.
#       → Incluye suma total de multas pendientes.
#         Template: reporte_morosos.html
#
#   busqueda_global(request) ← REQUIERE LOGIN
#       → Busca simultáneamente en libros y alumnos con el mismo término "q".
#       → LIBROS: busca en título, ISBN, nombre/apellido de autor (máx 10).
#       → ALUMNOS: busca en nombre, apellido, carnet o email (máx 10).
# =============================================================================
