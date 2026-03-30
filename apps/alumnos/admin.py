from django.contrib import admin
from django.contrib.auth.admin import UserAdmin, GroupAdmin
from django.contrib.auth.models import User, Group
from .models import Alumno


class SuperuserOnlyMixin:
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


admin.site.unregister(User)
admin.site.unregister(Group)


@admin.register(User)
class UserAdminRestringido(SuperuserOnlyMixin, UserAdmin):
    pass


@admin.register(Group)
class GroupAdminRestringido(SuperuserOnlyMixin, GroupAdmin):
    pass


@admin.register(Alumno)
class AlumnoAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre", "carnet", "email", "estado", "fecha_inscripcion")
    list_filter = ("estado",)
    search_fields = ("apellido", "nombre", "carnet", "email")


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/alumnos/admin.py
# =============================================================================
# Configura el admin para alumnos y restringe la gestión de usuarios/grupos.
#
# CLASE MIXIN:
#   SuperuserOnlyMixin → bloquea todas las operaciones (ver, añadir, cambiar,
#                        eliminar) para cualquier usuario que NO sea superusuario.
#                        Se reutiliza en UserAdminRestringido y GroupAdminRestringido.
#
# CLASES ADMIN:
#   UserAdminRestringido  → reemplaza el UserAdmin por defecto de Django.
#                           Solo superusuarios pueden gestionar usuarios del sistema.
#   GroupAdminRestringido → igual para los grupos de permisos.
#   AlumnoAdmin           → lista con filtro por estado (activo/inactivo/suspendido)
#                           y búsqueda por apellido, nombre, carnet o email.
#
# NOTA:
#   Se hace unregister de User y Group para registrarlos con el mixin aplicado,
#   evitando que un bibliotecario pueda crear o modificar usuarios del sistema.
# =============================================================================
