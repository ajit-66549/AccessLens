from django.contrib.auth import authenticate
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from rest_framework_simplejwt.tokens import RefreshToken

from .cookies import auth_auth_cookies, clear_auth_cookies
from .throttles import LoginRateThrottle, RefreshRateThrottle

# Create your views here.
class LoginView(APIView):
    authentication_classes = []     # to skip the global authentication
    permission_classes = [permissions.AllowAny]
    throttle_classes = [LoginRateThrottle]
    
    def post(self, request):
        username = request.data.get("username")
        password = request.data.get("password")
        
        user = authenticate(request, username=username, password=password)
        if not user:
            return Response({"detail": "Invalid Credentials"}, status=status.HTTP_401_UNAUTHORIZED)
        
        refresh = RefreshToken.for_user(user)
        access = str(refresh.access_token)
        
        res = Response({"Login": True})
        auth_auth_cookies(res, access_token=access, refresh_token=str(refresh))
        return res
    
class RefreshView(APIView):
    authentication_classes = []     # to skip the global authentication
    permission_classes = [permissions.AllowAny]
    throttle_classes = [RefreshRateThrottle]
    
    def post(self, request):
        refresh_token = request.COOKIES.get("refresh")
        
        if not refresh_token:
            return Response({"detail": "Refresh cookie missing"}, status=status.HTTP_401_UNAUTHORIZED)
        
        try:
            refresh = RefreshToken(refresh_token)
            access = str(refresh.access_token)
            
            refresh.set_jti()
            refresh.set_exp()
            
            res = Response({"Refresh": True})
            auth_auth_cookies(res, access_token=access, refresh_token=str(refresh))
            return res
        except Exception:
            return Response({"detail": "Invalid Refresh Token"}, status=status.HTTP_401_UNAUTHORIZED)
    
class LogoutView(APIView):
    def post(self, request):
        res = Response({"Logout": True})
        clear_auth_cookies(res)
        return res        