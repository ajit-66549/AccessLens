from rest_framework.permissions import BasePermission

class HasAppApiKey(BasePermission):
    def has_permission(self, request, view):
        return getattr(request, "api_key", None) is not None
