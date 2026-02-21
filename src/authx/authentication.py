from rest_framework import exceptions
from rest_framework.authentication import CSRFCheck
from rest_framework_simplejwt.authentication import JWTAuthentication

class CookieJWTAuthentication(JWTAuthentication):
    """
    Read JWT from cookies and enforce CSRF on unsafe methods.
    """
    def enforceCSRF(self, request):
        check = CSRFCheck(lambda req: None) # instantiate CSRF middleware, and (no ned to call next handler)
        check.process_request(request)  # read the CSRF token and attach to request object
        reason = check.process_view(request, None, (), {})  # validate csrf token
        if reason:
            raise exceptions.PermissionDenied(f"CSRF Failed {reason}")
    
    def authenticate(self, request):
        raw_token = request.COOKIES.get("access")
        if not raw_token:
            return None
        
        validated_token = self.get_validated_token(raw_token)
        user = self.get_user(validated_token)
        
        # enforce CSRF validation for updating methods
        if request.method not in ("GET", "HEAD", "OPTIONS", "TRACE"):
            self.enforceCSRF(request)
            
        return (user, validated_token)