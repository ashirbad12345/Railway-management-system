from django.contrib import admin
from django.conf import settings
from django.urls import include, path, re_path
from django.views.static import serve

from railways.views import AdminDashboardView, DashboardView

urlpatterns = [
    path("", DashboardView.as_view(), name="dashboard"),
    path("admin-dashboard/", AdminDashboardView.as_view(), name="admin-dashboard"),
    path("admin/", admin.site.urls),
    path("api/", include("railways.urls")),
    re_path(r"^static/(?P<path>.*)$", serve, {"document_root": settings.BASE_DIR / "railways" / "static"}),
]
