import uuid
from django.db import models
from django.conf import settings

from orgs.models import Organization

# Create your models here.
class AuditEvent(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="audit_events")
    actor = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="audit_events")
    action = models.CharField(max_length=50)
    target_type = models.CharField(max_length=50)
    target_id = models.UUIDField(null=True, blank=True)
    
    meta = models.JSONField(default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=["organization", "created_at"]),
            models.Index(fields=["organization", "action"]),
            models.Index(fields=["organization", "target_type", "target_id"]),
        ]
        
    def __str__(self):
        return f"{self.organization.slug} {self.action} {self.target_type}: {self.target_id}"