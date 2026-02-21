from django.conf import settings

ACCESS_COOKIE = "access"
REFRESH_COOKIE = "refresh"

def auth_auth_cookies(response, access_token: str, refresh_token: str) -> None:
    """
    Stores JWT in httponly cookies
    Access token sent to all routes
    refresh token sent to only api/auth/* routes
    """
    cookie_settings = settings.AUTH_COOKIE_SETTINGS
    
    # set access token
    response.set_cookie(
        ACCESS_COOKIE,
        access_token,
        httponly=True,
        secure=cookie_settings["access_secure"],
        samesite=cookie_settings["samesite"],
        path="/",
    )
    # set refresh token
    response.set_cookie(
        REFRESH_COOKIE,
        refresh_token,
        httponly=True,
        secure=cookie_settings["access_secure"],
        samesite=cookie_settings["samesite"]
        path="/api/auth/",   # refresh cookie only sent to auth endpoints
    )

def clear_auth_cookies(response) -> None:
    response.delete_cookie(ACCESS_COOKIE, path="/")
    response.delete_cookie(REFRESH_COOKIE, path="/api/auth/")