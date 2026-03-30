from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Crea el grupo 'Bibliotecario' con sus permisos correspondientes."

    def handle(self, *args, **kwargs):
        group, created = Group.objects.get_or_create(name="Bibliotecario")

        modelos = [
            ("alumnos", "alumno"),
            ("libros", "libro"),
            ("libros", "autor"),
            ("libros", "categoria"),
            ("libros", "libroautor"),
            ("libros", "librocategoria"),
            ("prestamos", "prestamo"),
        ]

        permisos = []
        for app, model in modelos:
            ct = ContentType.objects.get(app_label=app, model=model)
            for accion in ["add", "change", "delete", "view"]:
                permisos.append(
                    Permission.objects.get(content_type=ct, codename=f"{accion}_{model}")
                )

        group.permissions.set(permisos)

        accion = "creado" if created else "actualizado"
        self.stdout.write(self.style.SUCCESS(f'Grupo "Bibliotecario" {accion}.'))
        self.stdout.write(f"  Permisos asignados: {len(permisos)}")
        self.stdout.write("")
        self.stdout.write("Para asignar el rol a un usuario ve al admin:")
        self.stdout.write("  Autenticación > Usuarios > [usuario] > Grupos > Bibliotecario")
        self.stdout.write("  Asegúrate de que tenga 'is_staff = True' y 'is_superuser = False'")


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/alumnos/management/commands/crear_roles.py
# =============================================================================
# Comando de gestión Django para crear el grupo "Bibliotecario" con permisos.
# Se ejecuta con: python manage.py crear_roles
#
# QUÉ HACE:
#   · Crea (o actualiza) el grupo "Bibliotecario".
#   · Le asigna permisos CRUD completos (add/change/delete/view) sobre:
#       Alumno, Libro, Autor, Categoria, LibroAutor, LibroCategoria, Prestamo.
#   · NO incluye permisos sobre Multa (esas solo las gestiona el superusuario).
#
# CUÁNDO USARLO:
#   · Una sola vez después de las migraciones iniciales, o al actualizar permisos.
#   · Es idempotente: si el grupo ya existe, actualiza sus permisos sin duplicar.
#
# PARA ASIGNAR EL ROL A UN USUARIO:
#   Admin → Autenticación > Usuarios > [usuario] > Grupos > Bibliotecario
#   El usuario también necesita is_staff = True e is_superuser = False.
# =============================================================================
