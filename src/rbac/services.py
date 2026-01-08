from typing import Set
from orgs.models import Membership

def get_membership_role_keys(membership: Membership) -> Set[str]:
    """
    Arguments:
    membership
    
    Return:
    returns key of all roles in that membership
    """
    return {ra.role.key for ra in membership.role_assignments.select_related("role").all()}

def membership_has_any_role(membership: Membership, allowed: Set[str]) -> bool:
    """
    Arguments:
    membership and set of allowed roles in that membership
    
    Return:
    True if membership has at least one allowed role
    """
    role_keys = get_membership_role_keys(membership)
    return len(role_keys.intersection(allowed)) > 0