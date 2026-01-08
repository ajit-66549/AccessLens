from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.views import APIView

from .permissions import IsOrgAdminOrOwner
from .services import membership_has_any_role

# Create your views here.
class WhoAmIScopedView(APIView):
    permission_classes = [IsOrgAdminOrOwner]
    
    def get(self, request):
        roles = sorted(list(membership_has_any_role(request.membership)))
        return Response({
            "user": request.user.username,
            "org": request.org.slug,
            "roles": roles,
            "access": "admin_or_owner",
        })