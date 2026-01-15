from rest_framework.views import APIView
from rest_framework.response import Response

from .models import AuditEvent
from .serializers import AuditEventSerialzer
from rbac.permissions import IsOrgAdminOrOwner

# Create your views here.
class AuditListView(APIView):
    permission_classes = [IsOrgAdminOrOwner]
    
    def get(self, request):
        qs = AuditEvent.objects.filter(organization=request.org).select_related("actor").order_by("-created_at")
        return Response(AuditEventSerialzer(qs, many=True).data)