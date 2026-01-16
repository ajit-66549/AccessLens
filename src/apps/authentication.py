from rest_framework.authentication import BaseAuthentication
from rest_framework.exceptions import AuthenticationFailed

from .models import Apikey

class AppApiKeyAuthentication(BaseAuthentication):
    """
    Authorization: Bearer <api_key>
    """
    keyword = "Bearer"
    
    def authenticate(self, request):
        auth = request.headers.get("Authorization", "")
        if not auth:
            return None
        
        parts = auth.split(" ", 1)  # ["Bearer", api_key]
        
        if len(parts) != 2 or parts[0] != self.keyword:
            return None
        
        # get the raw key from the header
        raw_key = parts[1].strip()
        if not raw_key:
            raise AuthenticationFailed("Invalid Api Key")
        
        key_hash = Apikey.hash_key(raw_key)
        
        api_key = (Apikey.objects
                         .select_related("app__project__organization")
                         .filter(key_hash=key_hash, is_active=True, revoked_at__isnull=True)
                         .first())
        
        if not api_key:
            raise AuthenticationFailed("Invalid or revoked API key.")
        
        request.api_key = api_key
        request.app = api_key.app
        request.project = api_key.app.project
        request.org = api_key.app.project.organization
        
        return (None, api_key)