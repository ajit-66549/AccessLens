from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOrgAdminOrOwner
from .services import get_membership_role_keys

# Create your views here.
class WhoAmIScopedView(APIView):
    permission_classes = [IsOrgAdminOrOwner]
    
    def get(self, request):
        roles = sorted(get_membership_role_keys(request.membership))
        return Response({
            "user": request.user.username,
            "org": request.org.slug,
            "membership_id": request.membership.id,
            "roles": roles,
            "access": "admin_or_owner",
        })