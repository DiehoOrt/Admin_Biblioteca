from datetime import date
from django.contrib import admin
from .models import Multa


@admin.action(description="Marcar como pagada")
def marcar_pagada(modeladmin, request, queryset):
    pagadas = queryset.filter(estado=Multa.ESTADO_PENDIENTE).update(
        estado=Multa.ESTADO_PAGADA,
        fecha_pago=date.today(),
    )
    modeladmin.message_user(request, f"{pagadas} multa(s) marcadas como pagadas.")


@admin.register(Multa)
class MultaAdmin(admin.ModelAdmin):
    def has_module_perms(self, request):
        return request.user.is_superuser

    def has_view_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_add_permission(self, request):
        return request.user.is_superuser

    def has_change_permission(self, request, obj=None):
        return request.user.is_superuser

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    list_display = ("id", "prestamo", "monto", "motivo", "estado", "fecha_pago")
    list_filter = ("estado",)
    search_fields = ("prestamo__alumno__apellido", "prestamo__alumno__carnet")
    raw_id_fields = ("prestamo",)
    actions = [marcar_pagada]


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/multas/admin.py
# =============================================================================
# Configura el admin de multas, accesible SOLO para superusuarios.
#
# ACCIÓN marcar_pagada:
#   → Selección masiva para marcar multas PENDIENTES como pagadas (fecha = hoy).
#   → Usa .update() directo en el queryset (no dispara signals).
#
# CLASE MultaAdmin:
#   → Todos los métodos de permisos devuelven False si no es superusuario.
#   → Búsqueda por apellido o carnet del alumno dueño de la multa.
#   → Filtro lateral por estado (pendiente/pagada/anulada).
#   → raw_id_fields para prestamo: evita cargar todo el select con muchos registros.
#
# NOTA:
#   La generación de multas es AUTOMÁTICA desde prestamos/models.py (signal).
#   El admin solo sirve para consulta y para anular multas manualmente.
# =============================================================================
