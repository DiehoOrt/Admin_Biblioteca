from django.contrib import admin
from django.utils.html import format_html
from .models import Autor, Categoria, Libro, LibroAutor, LibroCategoria


class LibroAutorInline(admin.TabularInline):
    model = LibroAutor
    extra = 1


class LibroCategoriaInline(admin.TabularInline):
    model = LibroCategoria
    extra = 1


@admin.register(Libro)
class LibroAdmin(admin.ModelAdmin):
    list_display = ("portada_thumb", "titulo", "isbn", "anio_publicacion", "cantidad_total", "cantidad_disponible")
    search_fields = ("titulo", "isbn")
    inlines = [LibroAutorInline, LibroCategoriaInline]

    def portada_thumb(self, obj):
        if obj.portada:
            return format_html('<img src="{}" style="height:48px;border-radius:4px;">', obj.portada.url)
        return "—"
    portada_thumb.short_description = "Portada"


@admin.register(Autor)
class AutorAdmin(admin.ModelAdmin):
    list_display = ("apellido", "nombre")
    search_fields = ("apellido", "nombre")


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = ("nombre", "descripcion")
    search_fields = ("nombre",)


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/libros/admin.py
# =============================================================================
# Registra los modelos de libros en el panel de administración Django/Jazzmin.
#
# INLINES (se muestran dentro del formulario de Libro):
#   LibroAutorInline    → permite añadir/quitar autores directamente al editar
#                         un libro, sin salir al modelo intermedio.
#   LibroCategoriaInline→ igual pero para categorías.
#
# CLASES ADMIN:
#   LibroAdmin     → lista con thumbnail de portada (portada_thumb), título,
#                    ISBN, año, stock total y disponible.
#                    Búsqueda por título e ISBN.
#   AutorAdmin     → lista y búsqueda por apellido y nombre.
#   CategoriaAdmin → lista y búsqueda por nombre.
#
# MÉTODO ESPECIAL:
#   portada_thumb() → genera un <img> HTML con la portada en 48px de alto.
#                     Si no hay portada muestra "—".
# =============================================================================
