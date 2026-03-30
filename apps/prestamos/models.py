from datetime import date, timedelta
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from apps.alumnos.models import Alumno
from apps.libros.models import Libro

DIAS_PRESTAMO_DEFAULT = 15
MONTO_POR_DIA_RETRASO = 1.00


class Prestamo(models.Model):
    ESTADO_ACTIVO = "activo"
    ESTADO_DEVUELTO = "devuelto"
    ESTADO_VENCIDO = "vencido"
    ESTADOS = [
        (ESTADO_ACTIVO, "Activo"),
        (ESTADO_DEVUELTO, "Devuelto"),
        (ESTADO_VENCIDO, "Vencido"),
    ]

    alumno = models.ForeignKey(Alumno, on_delete=models.PROTECT, related_name="prestamos")
    libro = models.ForeignKey(Libro, on_delete=models.PROTECT, related_name="prestamos")
    fecha_prestamo = models.DateField(auto_now_add=True)
    fecha_devolucion_esperada = models.DateField()
    fecha_devolucion_real = models.DateField(null=True, blank=True)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_ACTIVO)

    class Meta:
        verbose_name = "Préstamo"
        verbose_name_plural = "Préstamos"
        ordering = ["-fecha_prestamo"]

    def __str__(self):
        return f"Préstamo #{self.pk} - {self.alumno} / {self.libro}"

    def save(self, *args, **kwargs):
        # Auto-fill fecha_devolucion_esperada al crear
        if not self.pk and not self.fecha_devolucion_esperada:
            self.fecha_devolucion_esperada = date.today() + timedelta(days=DIAS_PRESTAMO_DEFAULT)
        # Si tiene fecha_devolucion_real siempre es devuelto, sin importar si estaba vencido
        if self.fecha_devolucion_real:
            self.estado = self.ESTADO_DEVUELTO
        super().save(*args, **kwargs)


@receiver(pre_save, sender=Prestamo, dispatch_uid="prestamo_capture_old_estado")
def capture_old_estado(sender, instance, **kwargs):
    """Guarda el estado anterior para detectar la transición a devuelto."""
    if instance.pk:
        try:
            instance._old_estado = Prestamo.objects.values_list(
                "estado", flat=True
            ).get(pk=instance.pk)
        except Prestamo.DoesNotExist:
            instance._old_estado = None
    else:
        instance._old_estado = None


@receiver(post_save, sender=Prestamo, dispatch_uid="prestamo_post_save")
def prestamo_post_save(sender, instance, created, **kwargs):
    old_estado = getattr(instance, "_old_estado", None)

    if created:
        # Nuevo préstamo → decrementar disponibilidad
        instance.libro.cantidad_disponible = max(0, instance.libro.cantidad_disponible - 1)
        instance.libro.save(update_fields=["cantidad_disponible"])

    elif instance.estado == Prestamo.ESTADO_DEVUELTO and old_estado != Prestamo.ESTADO_DEVUELTO:
        # Transición a devuelto → devolver disponibilidad
        instance.libro.cantidad_disponible += 1
        instance.libro.save(update_fields=["cantidad_disponible"])

        # Generar multa automáticamente si fue tardío
        from apps.multas.models import Multa
        fecha_real = instance.fecha_devolucion_real
        if fecha_real and fecha_real > instance.fecha_devolucion_esperada:
            dias = (fecha_real - instance.fecha_devolucion_esperada).days
            if not Multa.objects.filter(prestamo=instance).exists():
                Multa.objects.create(
                    prestamo=instance,
                    monto=round(dias * MONTO_POR_DIA_RETRASO, 2),
                    motivo=f"Devolución tardía: {dias} día(s) de retraso",
                )


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/prestamos/models.py
# =============================================================================
# Define la lógica central de préstamos y la automatización mediante signals.
#
# CONSTANTES:
#   DIAS_PRESTAMO_DEFAULT = 15   → plazo estándar de devolución.
#   MONTO_POR_DIA_RETRASO = 1.00 → multa por cada día de retraso ($1.00/día).
#
# MODELO:
#   Prestamo → Registro de un préstamo. Vincula un Alumno con un Libro.
#              Fechas: prestamo (auto), devolucion_esperada (+15 días por defecto),
#                      devolucion_real (null hasta que se devuelva).
#              Estado: ACTIVO → VENCIDO (automático) → DEVUELTO (al registrar fecha real).
#
# MÉTODO Prestamo.save():
#   - Si es nuevo y no tiene fecha esperada, la calcula como hoy + 15 días.
#   - Si ya tiene fecha_devolucion_real, fuerza el estado a DEVUELTO.
#
# SIGNALS (automáticos, se disparan al guardar):
#   capture_old_estado   → pre_save: guarda el estado anterior para detectar
#                          si el préstamo acaba de pasar a DEVUELTO.
#   prestamo_post_save   → post_save:
#       · Si es NUEVO: decrementa libro.cantidad_disponible en 1.
#       · Si pasa a DEVUELTO: incrementa disponibilidad + genera Multa
#         automáticamente si la devolución fue tardía.
# =============================================================================
