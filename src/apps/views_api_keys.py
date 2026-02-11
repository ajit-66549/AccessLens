from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone

from orgs.permissions import HasOrgMembership
from rbac.permissions import IsOrgAdminOrOwner
from .models import App, Apikey

from apps.authentication import AppApiKeyAuthentication
from rest_framework.permissions import IsAuthenticated
from .permissions import HasAppApiKey

def SerializeApiKey(api_key: Apikey) -> dict:
    return {
        "id": str(api_key.id),
        "name": api_key.name,
        "app_id": str(api_key.app_id),
        "is_active": api_key.is_active,
        "created_at": api_key.created_at,
        "revoked_at": api_key.revoked_at,
        "created_by": str(api_key.created_by_id) if api_key.created_by_id else None,
    }

class ApiKeyListCreateView(APIView):
    """"
    Create an api key and return raw key
    """
    permission_classes = [IsOrgAdminOrOwner]
    
    # give the app with the given id 
    def get_app(self, request, app_id):
        try:
            app = App.objects.select_related("project__organization").get(id=app_id)
        except App.DoesNotExist:
            return Response({"detail": "App Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        # check if the app is in this organization
        if app.project.organization_id != request.org.id:
            return Response({"detail": "App is not in this organization"}, status=status.HTTP_403_FORBIDDEN)
        
        return app, None
    
    # lists all the api_keys in the app
    def get(self, request, app_id):
        apps, error_message = self.get_app(request, app_id)
        
        if error_message:
            return error_message
        
        api_keys = Apikey.objects.filter(app=apps).select_related("created_by").order_by("-created.at")
        return Response([SerializeApiKey(api_key) for api_key in api_keys])
    
    def post(self, request, app_id):
        app, error_message = self.get_app(request, app_id)
        if error_message:
            return error_message
        
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

# disable the api_key
class ApiKeyRevokeView(APIView):
    permission_classes = [IsOrgAdminOrOwner]
    
    def post(self, request, app_id, key_id):
        try:
            app = App.objects.select_related("project__organization").get(id=app_id)
        except App.DoesNotExist:
            return Response({"detail": "App Does Not Exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if app.project.organization_id != request.org.id:
            return Response({"detail": "App does not delong to this organization"}, status=status.HTTP_403_FORBIDDEN)
        
        # get the api key with thegiven key id in the given app
        api_key = Apikey.objects.filter(app=app, id=key_id).first()
        
        # if no api_key, return message
        if not api_key:
            return Response({"detail": "Api Key Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        # check if the api_key is already revoked
        if api_key.revoked_at:
            return Response({"deatil": "Api Key is already revoked", "api_key": SerializeApiKey(api_key)}, status=status.HTTP_200_OK)
        
        # revoke the api key
        api_key.is_active = False
        api_key.revoked_at = timezone.now() 
        api_key.save(update_fields=["is_active", "revoked_at"])
        
        return Response({"detail": "Apikey revoked.", "api_key": SerializeApiKey(api_key)}, status=status.HTTP_200_OK)
        
# creates a new api_key for the app, and revokes the old one
class ApiKeyRotateView(APIView):
    permission_classes = [IsOrgAdminOrOwner]
    
    def post(self, request, app_id, key_id):
        try:
            app = App.objects.select_related("project__organization").get(app=app_id)
        except App.DoesNotExist:
            return Response({"deatil": "App does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
        if app.project.organization_id != request.org.id:
            return Response({"detail": "App doesn't belong to this organization"}, status=status.HTTP_403_FORBIDDEN)
        
        # get the old api key 
        old_key = Apikey.objects.filter(app=app, id=key_id).first()
        if not old_key:
            return Response({"detail": "Api Key Not Found"}, status=status.HTTP_404_NOT_FOUND)
        
        if old_key.revoked_at:
            return Response({"deatil": "Api Key is already revoked"}, status=status.HTTP_200_OK)
        
        name = request.data.get("name", "").strip() or old_key.name
        
        raw_key = Apikey.generate_api_key()
        hash_key = Apikey.hash_key(raw_key)
        
        new_key = Apikey.objects.create(app=app, key_hash=hash_key, name=name, created_by=request.user if request.user.is_authenticated else None,)
        
        old_key.is_active = False
        old_key.revoked_at = timezone.now()
        old_key.save(update_fields=["is_active", "revoked_at"])
        
        return Response({
            "detail": "Api key rotated",
            "raw_key": raw_key,
            "api_key": SerializeApiKey(new_key),
            "revoked_key": SerializeApiKey(old_key),
            }, status=status.HTTP_201_CREATED)

class ApiKeyPingView(APIView):
    authentication_classes = [AppApiKeyAuthentication]
    permission_classes = [HasAppApiKey]
    
    def get(self, request):
        return Response({
            "ok": True,
            "app_id": str(request.app.id),
            "project_id": str(request.project.id),
            "org_slug": request.org.slug,
        })