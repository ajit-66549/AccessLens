from rest_framework.permissions import BasePermission
from orgs.permissions import HasOrgMembership
from .services import membership_has_any_role


class HasOrgRole(BasePermission):
    allowed_roles = set()
    message = "You do not have permission to perform this action in this organization."

    def has_permission(self, request, view):
        # Ensure org + membership context exists
        if not HasOrgMembership().has_permission(request, view):
            self.message = HasOrgMembership.message
            return False

        # Role check using service (single source of truth)
        return membership_has_any_role(request.membership, self.allowed_roles)


class IsOrgOwner(HasOrgRole):
    allowed_roles = {"owner"}


class IsOrgAdminOrOwner(HasOrgRole):
    allowed_roles = {"admin", "owner"}

class IsOrgMember(HasOrgRole):
    allowed_roles = {"admin", "owner", "viewer"}
