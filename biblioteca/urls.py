from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.urls import include, path
from . import views

admin.site.login_url = '/login/'

urlpatterns = [
    path("", views.home_view, name="home"),
    path("catalogo/", views.catalogo_publico, name="catalogo"),
    path("dashboard/", views.dashboard, name="dashboard"),
    path("login/", auth_views.LoginView.as_view(template_name="login.html"), name="login"),
    path("logout/", auth_views.LogoutView.as_view(), name="logout"),
    path("alumnos/", include("apps.alumnos.urls")),
    path("libros/", include("apps.libros.urls")),
    path("buscar/", views.busqueda_global, name="busqueda"),
    path("reporte/morosos/", views.reporte_morosos, name="reporte_morosos"),
    path("admin/", admin.site.urls),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


# =============================================================================
# RESUMEN DEL ARCHIVO: biblioteca/urls.py
# =============================================================================
# Archivo central de rutas del proyecto. Conecta todas las URLs.
#
#   /               → home_view       (redirige a dashboard o login según auth)
#   /catalogo/      → catalogo_publico (no requiere login)
#   /dashboard/     → dashboard        (requiere login)
#   /login/         → LoginView de Django (template: login.html)
#   /logout/        → LogoutView de Django
#   /alumnos/       → incluye apps/alumnos/urls.py
#   /libros/        → incluye apps/libros/urls.py
#   /buscar/        → busqueda_global  (requiere login)
#   /reporte/morosos/ → reporte_morosos (requiere login)
#   /admin/         → panel Django/Jazzmin
#
# NOTA:
#   admin.site.login_url = '/login/' redirige al login personalizado en vez del
#   login por defecto del admin cuando un usuario no autenticado accede al admin.
#   + static(...) agrega la URL de media solo en desarrollo (DEBUG=True).
# =============================================================================
