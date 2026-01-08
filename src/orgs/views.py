from django.shortcuts import render
from .serializers import CurrentOrgSerializer
from .permissions import HasOrgMembership

from rest_framework.views import APIView
from rest_framework.response import Response

# Create your views here.
class CurrentOrgView(APIView):
    permission_classes = [HasOrgMembership]
    
    def get(self, request):
        payload = { # our request has organization and membership -> which helps to get the values
            "org_id": request.org.id,
            "name": request.org.name,
            "slug": request.org.slug,
            "membership_id": request.membership.id,
            "is_active": request.membership.is_active,
        }
        return Response(CurrentOrgSerializer(payload).data)