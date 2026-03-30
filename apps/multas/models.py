from django.db import models
from apps.prestamos.models import Prestamo


class Multa(models.Model):
    ESTADO_PENDIENTE = "pendiente"
    ESTADO_PAGADA = "pagada"
    ESTADO_ANULADA = "anulada"
    ESTADOS = [
        (ESTADO_PENDIENTE, "Pendiente"),
        (ESTADO_PAGADA, "Pagada"),
        (ESTADO_ANULADA, "Anulada"),
    ]

    prestamo = models.OneToOneField(Prestamo, on_delete=models.PROTECT, related_name="multa")
    monto = models.DecimalField(max_digits=8, decimal_places=2)
    motivo = models.CharField(max_length=255)
    estado = models.CharField(max_length=20, choices=ESTADOS, default=ESTADO_PENDIENTE)
    fecha_pago = models.DateField(null=True, blank=True)

    class Meta:
        verbose_name = "Multa"
        verbose_name_plural = "Multas"
        ordering = ["-id"]

    def __str__(self):
        return f"Multa #{self.pk} - {self.prestamo} / ${self.monto}"


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/multas/models.py
# =============================================================================
# Define la tabla de multas generadas por devoluciones tardías.
#
# MODELO:
#   Multa → Se crea automáticamente desde el signal prestamo_post_save cuando
#           un libro se devuelve después de la fecha esperada.
#           Campos: prestamo (OneToOne), monto ($1 × días de retraso),
#                   motivo (texto descriptivo), estado y fecha_pago.
#
# ESTADOS POSIBLES:
#   pendiente → recién generada, bloquea nuevos préstamos al alumno.
#   pagada    → liquidada por el alumno (staff la marca desde el perfil o admin).
#   anulada   → cancelada manualmente por el superusuario.
#
# NOTA:
#   Solo superusuarios pueden ver y gestionar multas en el admin.
#   Los bibliotecarios solo las ven en el perfil del alumno y pueden marcarlas
#   como pagadas desde alumnos/views.py → pagar_multa().
# =============================================================================
