from django.db import models


class Autor(models.Model):
    nombre = models.CharField(max_length=100)
    apellido = models.CharField(max_length=100)

    class Meta:
        verbose_name = "Autor"
        verbose_name_plural = "Autores"
        ordering = ["apellido", "nombre"]

    def __str__(self):
        return f"{self.apellido}, {self.nombre}"


class Categoria(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = "Categoría"
        verbose_name_plural = "Categorías"
        ordering = ["nombre"]

    def __str__(self):
        return self.nombre


class Libro(models.Model):
    titulo = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20, unique=True)
    anio_publicacion = models.PositiveIntegerField()
    cantidad_total = models.PositiveIntegerField(default=1)
    cantidad_disponible = models.PositiveIntegerField(default=1)
    descripcion = models.TextField(blank=True, verbose_name="Descripción")
    portada = models.ImageField(upload_to="portadas/", null=True, blank=True)
    autores = models.ManyToManyField(Autor, through="LibroAutor", related_name="libros")
    categorias = models.ManyToManyField(Categoria, through="LibroCategoria", related_name="libros")

    class Meta:
        verbose_name = "Libro"
        verbose_name_plural = "Libros"
        ordering = ["titulo"]

    def __str__(self):
        return self.titulo


class LibroAutor(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    autor = models.ForeignKey(Autor, on_delete=models.CASCADE)

    class Meta:
        db_table = "libros_libro_autor"
        unique_together = ("libro", "autor")


class LibroCategoria(models.Model):
    libro = models.ForeignKey(Libro, on_delete=models.CASCADE)
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE)

    class Meta:
        db_table = "libros_libro_categoria"
        unique_together = ("libro", "categoria")


# =============================================================================
# RESUMEN DEL ARCHIVO: apps/libros/models.py
# =============================================================================
# Define las tablas de la base de datos relacionadas con el catálogo de libros.
#
# MODELOS:
#   Autor           → Persona que escribió el libro (nombre, apellido).
#   Categoria       → Clasificación del libro (Novela, Informática, etc.).
#   Libro           → Libro del catálogo. Almacena título, ISBN, año, stock total
#                     y stock disponible. La portada se guarda en media/portadas/.
#   LibroAutor      → Tabla intermedia M2M entre Libro y Autor.
#                     Permite que un libro tenga varios autores y viceversa.
#   LibroCategoria  → Tabla intermedia M2M entre Libro y Categoria.
#                     Permite que un libro tenga varias categorías.
#
# CAMPOS CLAVE:
#   Libro.cantidad_disponible → se decrementa al prestar y se incrementa al
#                               devolver, gestionado por signals en prestamos/models.py.
#   Libro.portada             → ImageField; requiere Pillow instalado.
# =============================================================================
