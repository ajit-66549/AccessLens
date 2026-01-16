from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from orgs.permissions import HasOrgMembership
from rbac.permissions import IsOrgAdminOrOwner
from .models import App, Apikey

class CreateApiKeyView(Apikey):
    """"
    Create an api key and return raw key
    """
    permission_classes = [IsOrgAdminOrOwner]
    
    def post(self, request, app_id):
        # get that app
        try:
            app = App.objects.select_related("project__organization").get(id=app_id)
        except App.DoesNotExist:
            return Response({"detail": "App Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        # check if the app is in this organization
        if app.project.organization_id != request.org.id:
            return Response({"detail": "App is not in this organization"}, status=status.HTTP_403_FORBIDDEN)
        
        name = request.data.get("name", "").strip()
        
        # generate raw key for app
        raw_key = Apikey.generate_api_key()
        
        # hash that raw key
        key_hash = Apikey.hash_key(raw_key)
        
        # Create an api key instance
        api_key = Apikey.objects.create(
            app=app,
            key_hash=key_hash,
            name=name,
            created_by=request.user if request.user.is_authenticated else None,
        )
        
        # Return raw key once
        return Response(
            {
                "id": str(api_key.id),
                "name": str(api_key.name),
                "app_id": str(app.id),
                "raw_key": raw_key,
            }, status=status.HTTP_201_CREATED,
        )