from rest_framework.views import APIView
from rest_framework.response import Response

from .models import AuditEvent
from .serializers import AuditEventSerialzer
from rbac.permissions import IsOrgAdminOrOwner

from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied

# Create your views here.

class IsOrgAdminOrOwnerOrApiKey(BasePermission):
    """
    Pass if:
    - API key auth was used (request.api_key exists) AND org is already resolved, OR
    - JWT user is org admin/owner (existing permission)
    """

    def has_permission(self, request, view):
        # --- API KEY path ---
        if getattr(request, "api_key", None) is not None:
            # Your AppApiKeyAuthentication should attach request.org
            if not getattr(request, "org", None):
                raise PermissionDenied("Valid X-Org-Slug header and active membership are required.")
            return True

        # --- JWT USER path (your existing logic) ---
        return IsOrgAdminOrOwner().has_permission(request, view)

class AuditListView(APIView):
    permission_classes = [IsOrgAdminOrOwnerOrApiKey]
    
    def get(self, request):
        qs = AuditEvent.objects.filter(organization=request.org).select_related("actor").order_by("-created_at")
        return Response(AuditEventSerialzer(qs, many=True).data)