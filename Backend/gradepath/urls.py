"""
URL configuration for gradepath project.
Serves both the Django REST API (at /api/) and the static Frontend HTML/CSS/JS files.
"""

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.static import serve
from django.http import HttpResponse, Http404
from django.conf import settings
import os


def serve_frontend_file(request, filename='index.html'):
    """Serve any HTML file from the Frontend directory."""
    filepath = os.path.join(str(settings.FRONTEND_DIR), filename)
    if not os.path.exists(filepath):
        raise Http404(f"Page '{filename}' not found.")
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    return HttpResponse(content, content_type='text/html')


urlpatterns = [
    # Django admin
    path("admin/", admin.site.urls),

    # REST API
    path("api/", include("api.urls")),

    # ── Static assets — served with no-cache so browsers always get fresh files ──
    re_path(r'^(?P<path>.*\.(css|js|png|jpg|jpeg|gif|ico|svg|webp|woff|woff2|ttf))$',
            serve, {'document_root': str(settings.FRONTEND_DIR)}),

    # ── Frontend HTML Pages ─────────────────────────────────────────────────
    path("", lambda req: serve_frontend_file(req, 'index.html'),                    name="home"),
    path("index.html", lambda req: serve_frontend_file(req, 'index.html'),          name="home_explicit"),
    path("register.html", lambda req: serve_frontend_file(req, 'register.html'),    name="register"),
    path("register/",     lambda req: serve_frontend_file(req, 'register.html'),    name="register_clean"),
    path("login_student.html", lambda req: serve_frontend_file(req, 'login_student.html'), name="login_student"),
    path("login-student/",     lambda req: serve_frontend_file(req, 'login_student.html'), name="login_student_clean"),
    path("login_admin.html",   lambda req: serve_frontend_file(req, 'login_admin.html'),   name="login_admin"),
    path("login-admin/",       lambda req: serve_frontend_file(req, 'login_admin.html'),   name="login_admin_clean"),
    path("courses.html",       lambda req: serve_frontend_file(req, 'courses.html'),        name="courses"),
    path("courses/",           lambda req: serve_frontend_file(req, 'courses.html'),        name="courses_clean"),
    path("customize.html",     lambda req: serve_frontend_file(req, 'customize.html'),      name="customize"),
    path("customize/",         lambda req: serve_frontend_file(req, 'customize.html'),      name="customize_clean"),
    path("plan_output.html",   lambda req: serve_frontend_file(req, 'plan_output.html'),    name="plan_output"),
    path("vault.html",         lambda req: serve_frontend_file(req, 'vault.html'),          name="vault"),
    path("vault/",             lambda req: serve_frontend_file(req, 'vault.html'),          name="vault_clean"),
    path("student_dashboard.html", lambda req: serve_frontend_file(req, 'student_dashboard.html'), name="student_dashboard"),
    path("dashboard/",             lambda req: serve_frontend_file(req, 'student_dashboard.html'), name="student_dashboard_clean"),
    path("admin_dashboard.html",   lambda req: serve_frontend_file(req, 'admin_dashboard.html'),   name="admin_dashboard"),
    path("admin-dashboard/",       lambda req: serve_frontend_file(req, 'admin_dashboard.html'),   name="admin_dashboard_clean"),
]
