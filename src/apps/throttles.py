from rest_framework.throttling import UserRateThrottle

class ApiKeyWriteRateThrottle(UserRateThrottle):
    scope = "api_keys_write"