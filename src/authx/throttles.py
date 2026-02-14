from rest_framework.throttling import AnonRateThrottle

class LoginRateThrottle(AnonRateThrottle):
    scope = "auth_login"
    
class RefreshRateThrottle(AnonRateThrottle):
    scope = "auth_refresh"