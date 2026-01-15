from uuid import UUID
from typing import Optional
from django.http import HttpRequest

from .models import AuditEvent
from orgs.models import Organization

# get user/client's ip address from the incoming request
def get_client_ip(request: HttpRequest) -> Optional[str]:
    return request.META.get("REMOTE_ADDR")

# return audit record
def write_audit_event(*, 
                      request: HttpRequest, 
                      organization: Organization, 
                      action: str, 
                      target_type: str, 
                      target_id: Optional[UUID] = None,
                      meta: Optional[dict] = None,
                      ) -> AuditEvent:
    actor = request.user if getattr(request, "user", None) and request.user.is_authenticated else None
    
    return AuditEvent.objects.create(
        organization=organization,
        actor=actor,
        action=action,
        target_type=target_type,
        target_id=target_id,
        meta=meta or {},
        ip_address = get_client_ip(request),
        user_agent = request.META.get("HTTP_USER_AGENT", ""),
    )    