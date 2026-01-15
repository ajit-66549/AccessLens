from rest_framework.permissions import BasePermission
from .models import Membership
from .services import get_current_org

class HasOrgMembership(BasePermission):
    """
    Requires:
    1) X-Org-Slug header is provided and valid
    2) request.user is an active member of that org

    Attaches:
    - request.org
    - request.membership
    """
    message = "Valid X-Org-Slug header and active membership are required."  # if the function returns False -> this message will be shown
    
    def has_permission(self, request, view):
        # get the resolved organization
        org = get_current_org(request)
        if not org:
            return False
        
        # check if authenticated user exist
        if not request.user or not request.user.is_authenticated:
            return False
        
        # get the membership of that user with that organization
        membership = (
            Membership.objects
            .select_related("organization", "user")
            .filter(user=request.user, organization=org, is_active=True)
            .first()
        )
        
        if not membership:
            return False
        
        # Attach org and membership in request for downstream use
        request.org = org
        request.membership = membership
        return True