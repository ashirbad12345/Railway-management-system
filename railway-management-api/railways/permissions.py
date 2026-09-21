from django.conf import settings
from rest_framework.permissions import BasePermission


class HasAdminAPIKey(BasePermission):
    message = "A valid admin API key is required."

    def has_permission(self, request, view):
        return bool(settings.ADMIN_API_KEY and request.headers.get("X-API-Key") == settings.ADMIN_API_KEY)
