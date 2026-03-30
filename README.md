# Sistema de Gestión de Biblioteca — UNICAES

Sistema web para gestionar préstamos de libros, alumnos, autores y categorías, desarrollado con Django y Jazzmin.

## Requisitos

- Python 3.11 o superior
- pip

## Instalación

### 1. Clonar el repositorio

```bash
git clone <https://github.com/DiehoOrt/Admin_Biblioteca.git>
cd GestionBiblioteca
```

### 2. Crear y activar el entorno virtual

**Linux / macOS:**
```bash
python -m venv venv
source venv/bin/activate
```

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Aplicar migraciones

```bash
python manage.py migrate
```

### 5. Crear roles

```bash
python manage.py crear_roles
```

### 6. Crear superusuario

```bash
python manage.py createsuperuser
```

### 7. Ejecutar el servidor

```bash
python manage.py runserver
```

Accede en: http://127.0.0.1:8000

## Roles

| Rol | Acceso |
|-----|--------|
| **Superusuario** | Todo el sistema — usuarios, multas, configuración |
| **Bibliotecario** | Alumnos, Libros, Autores, Categorías y Préstamos |

Para crear un bibliotecario: crear el usuario en el admin con `is_staff = True` y asignarle el grupo **Bibliotecario**.

## Módulos

- **Alumnos** — registro y gestión de alumnos
- **Libros** — catálogo con autores y categorías
- **Préstamos** — control de préstamos y devoluciones
- **Multas** — gestión de multas por devolución tardía (solo superusuario)

## Estructura del proyecto

```
GestionBiblioteca/
│
├── biblioteca/                 # Configuración principal del proyecto
│   ├── settings.py
│   ├── urls.py
│   └── views.py                # Dashboard y búsqueda global
│
├── apps/
│   ├── alumnos/
│   │   ├── models.py
│   │   ├── views.py
│   │   ├── admin.py            # Incluye restricción de Users/Groups al superusuario
│   │   ├── urls.py
│   │   └── management/
│   │       └── commands/
│   │           ├── crear_roles.py      # Crea el grupo Bibliotecario
│   │           └── poblar_datos.py     # Datos de prueba
│   ├── libros/
│   │   ├── models.py           # Libro, Autor, Categoria, LibroAutor, LibroCategoria
│   │   ├── views.py
│   │   ├── admin.py
│   │   └── urls.py
│   ├── prestamos/
│   │   ├── models.py
│   │   └── admin.py
│   └── multas/
│       ├── models.py
│       └── admin.py            # Restringido solo al superusuario
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── dashboard.html
│   ├── busqueda.html
│   ├── alumnos/
│   │   ├── lista.html
│   │   └── perfil.html
│   └── libros/
│       ├── lista.html
│       └── detalle.html
│
├── static/
│   ├── css/
│   │   ├── base.css
│   │   ├── dashboard.css
│   │   ├── login_custom.css
│   │   └── admin_custom.css    # Estilos del login del admin
│   ├── img/
│   │   ├── UNICAES_Logo.png
│   │   └── fondoUnicaes.png
│   └── js/
│       └── dashboard.js
│
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md
```

## Rutas y URLs

### Acceso general

| URL | Descripción | Requiere sesión |
|-----|-------------|-----------------|
| `/` | Redirige al login o al dashboard según sesión | No |
| `/login/` | Formulario de inicio de sesión | No |
| `/logout/` | Cierra la sesión y redirige al login | Sí |
| `/catalogo/` | Catálogo público de libros (apto para compartir) | No |
| `/dashboard/` | Panel principal con estadísticas y gráficas | Sí |
| `/buscar/` | Búsqueda global de libros y alumnos | Sí |
| `/reporte/morosos/` | Reporte de préstamos vencidos y multas pendientes | Sí |
| `/admin/` | Panel de administración (Jazzmin) | Sí (staff) |

### Libros

| URL | Descripción | Requiere sesión |
|-----|-------------|-----------------|
| `/libros/` | Lista de libros con búsqueda | Sí |
| `/libros/<id>/` | Detalle del libro, préstamos activos e historial | Sí |

### Alumnos

| URL | Descripción | Requiere sesión |
|-----|-------------|-----------------|
| `/alumnos/` | Lista de alumnos con búsqueda | Sí |
| `/alumnos/<id>/` | Perfil del alumno con préstamos y multas | Sí |
| `/alumnos/<id>/devolver/<prestamo_id>/` | Registrar devolución de libro (POST) | Sí |
| `/alumnos/<id>/pagar/<multa_id>/` | Marcar multa como pagada (POST) | Sí |

### Administración (acceso rápido)

| URL | Descripción |
|-----|-------------|
| `/admin/prestamos/prestamo/add/` | Crear nuevo préstamo |
| `/admin/libros/libro/` | Gestionar libros |
| `/admin/libros/autor/` | Gestionar autores |
| `/admin/libros/categoria/` | Gestionar categorías |
| `/admin/alumnos/alumno/` | Gestionar alumnos |
| `/admin/multas/multa/` | Gestionar multas (solo superusuario) |
| `/admin/auth/user/` | Gestionar usuarios (solo superusuario) |

## Documentación de archivos Python

| Archivo | Qué se explica |
|---------|----------------|
| `libros/models.py` | Para qué es cada modelo, qué es `cantidad_disponible` y por qué existe `LibroAutor`/`LibroCategoria` |
| `alumnos/models.py` | Significado de cada estado y cómo se usa en el sistema |
| `prestamos/models.py` | Las constantes de negocio, el método `save()` y los dos signals con su flujo |
| `multas/models.py` | Cómo se genera automáticamente, los estados y quién puede gestionarla |
| `libros/views.py` | Las dos vistas, dónde están los filtros/búsquedas y qué queries hace cada una |
| `alumnos/views.py` | Las 4 vistas, búsqueda con `annotate`, consultas de perfil, y cómo funcionan las acciones POST |
| `libros/admin.py` | Para qué sirven los inlines y el método `portada_thumb` |
| `alumnos/admin.py` | El mixin de superusuario, por qué se hace unregister/register de User y Group |
| `prestamos/admin.py` | Las 4 validaciones del form, la acción masiva y todos los métodos `get_*` |
| `multas/admin.py` | Por qué solo superusuarios, cómo funciona la acción y el rol del admin vs el signal |
| `alumnos/urls.py` | Las 4 rutas y el comportamiento de GET en acciones POST |
| `libros/urls.py` | Las 2 rutas |
| `biblioteca/urls.py` | Todas las rutas, la redirección del admin login y el `static()` solo en dev |
| `biblioteca/views.py` | Las funciones auxiliares, todas las consultas del dashboard (7 gráficos + 2 tablas) y los filtros del catálogo y búsqueda global |
| `crear_roles.py` | Qué permisos se asignan, cuándo correrlo y cómo asignar el rol |
| `poblar_datos.py` | Los 6 escenarios de préstamos, el truco del `.update()` para la fecha y la transacción atómica |

> Cada archivo contiene el detalle completo al final, en un bloque de comentarios `# ===`.

## Tecnologías

- Django 6.0.3
- django-jazzmin 3.0.4
- SQLite (base de datos por defecto)
- Bootstrap 5
