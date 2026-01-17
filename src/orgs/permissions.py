from rest_framework.permissions import BasePermission
from rest_framework.exceptions import PermissionDenied
from .models import Membership, Organization
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
    
class IsJwtUserOrApiKey(BasePermission):
    """
    Allow access if:-
    - request.user is authenticated (JWT cookie auth), OR
    - request.api_key exists (machine-to-machine auth)
    """
    def has_permission(self, request, view):
        # check for JWT User
        if getattr(request, "user", None) and request.user.is_authenticated:
            return True
        
        # check for Api key
        if getattr(request, "api_key", None) is not None:
            return True
        
        return False
    
class OrgScopedRequired(BasePermission):
    """
    Requires X-Org-Slug header.
    Then enforces:
    - If API key auth: request.org.slug must match X-Org-Slug
    - If JWT user auth: user must be active member in that org
    Also attaches request.org for JWT path.
    """
    header = "X-Org-Slug"
    
    def has_permission(self, request, view):
        org_slug = request.headers.get(self.header)
        if not org_slug:
            raise PermissionDenied("Valid X-Org-Slug header and active membership are required.")
        
        # JWT User Path
        if getattr(request, "user", None) and request.user_is_authenticated:
            # get the organization from header
            try:
                org = Organization.objects.get(slug=org_slug)
            except Organization.DoesNotExist:
                raise PermissionDenied("Valid X-Org-Slug header and active membership are required.")
            
            # check if the user is active member of the org
            is_member = Membership.objects.filter(organization = org, user=request.user, is_active=True).exists()
            
            if not is_member:
                raise PermissionDenied("Valid X-Org-Slug header and active membership are required.")
            
            # Attach org for downstream use
            request.org = org
            return True
        
        # Api Key Path
        if getattr(request, "api_key", None) is not None:
            req_org = getattr(request, "org", None)
            if not req_org or req_org.slug != org_slug:
                raise PermissionDenied("Valid X-Org-Slug header and active membership are required.")
            return True                
        
        return False
    