from datetime import date, timedelta
from django import forms
from django.contrib import admin
from django.utils.html import format_html
from .models import Prestamo, DIAS_PRESTAMO_DEFAULT
from apps.alumnos.models import Alumno


class PrestamoAdminForm(forms.ModelForm):
    class Meta:
        model = Prestamo
        fields = "__all__"

    def clean(self):
        cleaned_data = super().clean()
        alumno = cleaned_data.get("alumno")
        libro = cleaned_data.get("libro")

        if not self.instance.pk:  # Solo al crear
            if alumno:
                if alumno.estado != Alumno.ESTADO_ACTIVO:
                    raise forms.ValidationError(
                        f"El alumno {alumno} no está activo ({alumno.get_estado_display()})."
                    )
                from apps.multas.models import Multa
                if Multa.objects.filter(
                    prestamo__alumno=alumno, estado=Multa.ESTADO_PENDIENTE
                ).exists():
                    raise forms.ValidationError(
                        f"{alumno} tiene multas pendientes. Debe pagarlas antes de recibir un préstamo."
                    )
                prestamos_activos = Prestamo.objects.filter(
                    alumno=alumno,
                    estado__in=[Prestamo.ESTADO_ACTIVO, Prestamo.ESTADO_VENCIDO],
                ).count()
                if prestamos_activos >= 3:
                    raise forms.ValidationError(
                        f"{alumno} ya tiene {prestamos_activos} préstamo(s) activo(s). "
                        f"El límite es 3 libros simultáneos."
                    )
            if libro and libro.cantidad_disponible <= 0:
                raise forms.ValidationError(
                    f"'{libro}' no tiene ejemplares disponibles (stock: 0)."
                )
        return cleaned_data


@admin.action(description="Registrar devolución (hoy)")
def marcar_devuelto(modeladmin, request, queryset):
    devueltos = 0
    for prestamo in queryset.exclude(estado=Prestamo.ESTADO_DEVUELTO):
        prestamo.fecha_devolucion_real = date.today()
        prestamo.save()  # save() + signals manejan el resto automáticamente
        devueltos += 1
    modeladmin.message_user(request, f"{devueltos} préstamo(s) registrados como devueltos.")


@admin.register(Prestamo)
class PrestamoAdmin(admin.ModelAdmin):
    form = PrestamoAdminForm
    list_display = (
        "id", "alumno", "libro",
        "fecha_prestamo", "fecha_devolucion_esperada", "fecha_devolucion_real",
        "estado_badge",
    )
    list_filter = ("estado",)
    search_fields = ("alumno__apellido", "alumno__carnet", "libro__titulo", "libro__isbn")
    raw_id_fields = ("alumno", "libro")
    actions = [marcar_devuelto]

    def get_queryset(self, request):
        # Auto-actualizar préstamos vencidos antes de mostrar la lista
        Prestamo.objects.filter(
            estado=Prestamo.ESTADO_ACTIVO,
            fecha_devolucion_esperada__lt=date.today(),
        ).update(estado=Prestamo.ESTADO_VENCIDO)
        return super().get_queryset(request)

    def get_fields(self, _request, obj=None):
        if obj is None:  # Crear: solo alumno, libro y fecha esperada
            return ["alumno", "libro", "fecha_devolucion_esperada"]
        # Editar: solo se puede llenar fecha_devolucion_real
        return ["alumno", "libro", "fecha_prestamo", "fecha_devolucion_esperada", "fecha_devolucion_real", "estado"]

    def get_readonly_fields(self, _request, obj=None):
        if obj is None:
            return []
        # Al editar, todo es readonly excepto fecha_devolucion_real
        return ["alumno", "libro", "fecha_prestamo", "fecha_devolucion_esperada", "estado"]

    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj is None and "fecha_devolucion_esperada" in form.base_fields:
            form.base_fields["fecha_devolucion_esperada"].initial = (
                date.today() + timedelta(days=DIAS_PRESTAMO_DEFAULT)
            )
        return form

    def estado_badge(self, obj):
        colores = {
            Prestamo.ESTADO_ACTIVO: ("green", "Activo", ""),
            Prestamo.ESTADO_DEVUELTO: ("gray", "Devuelto", ""),
            Prestamo.ESTADO_VENCIDO: ("red", "⚠ Vencido", "font-weight:bold;"),
        }
        color, label, bold = colores.get(obj.estado, ("black", obj.estado, ""))
        return format_html('<span style="color:{};{}">{}</span>', color, bold, label)

    estado_badge.short_description = "Estado"


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/prestamos/admin.py
# =============================================================================
# Configura el admin de préstamos con validaciones, acciones y UI mejorada.
#
# FORMULARIO PrestamoAdminForm (validaciones al CREAR, no al editar):
#   · El alumno debe tener estado ACTIVO.
#   · El alumno no puede tener multas PENDIENTES.
#   · El alumno no puede tener más de 3 préstamos activos/vencidos simultáneos.
#   · El libro debe tener cantidad_disponible > 0.
#
# ACCIÓN marcar_devuelto:
#   → Permite seleccionar varios préstamos y registrar devolución masiva (hoy).
#   → Llama a prestamo.save() para que los signals actúen (disponibilidad + multa).
#
# CLASE PrestamoAdmin:
#   get_queryset()        → Auto-actualiza vencidos antes de mostrar la lista.
#   get_fields()          → Al CREAR muestra solo alumno, libro y fecha esperada.
#                           Al EDITAR muestra todos los campos.
#   get_readonly_fields() → Al editar, solo fecha_devolucion_real es editable.
#   get_form()            → Pre-rellena fecha_devolucion_esperada con hoy + 15 días.
#   estado_badge()        → Muestra el estado como texto con color:
#                           verde = activo, gris = devuelto, rojo = vencido.
# =============================================================================
