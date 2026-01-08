from typing import Optional
from .models import Organization
from django.http import HttpRequest

ORG_HEADER = "HTTP_X_ORG_SLUG"   # Django converts hyphen with underscore, set in uppercase, and add HTTP_ prefix

def get_current_org(request: HttpRequest) -> Optional[Organization]:
    """
    Resolve the current organization from the request header.
    Returns None if header is missing or invalid.
    """
    slug = request.META.get(ORG_HEADER)   # as Django stores header in request.META with HTTP_ prefix
    
    if not slug:          # if header doesn't have slug return None, no need to query much in database
        return None        
    try:
        return Organization.objects.get(slug=slug) # return the organization having that specified slug
    except Organization.DoesNotExist:              # return None if no organization with that slug exists
        return None