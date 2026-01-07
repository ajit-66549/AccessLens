from django.db import models
from django.conf import settings
import uuid

# Create your models here.
class Organization(models.Model):
    """
    A workspace
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=80, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
class Membership(models.Model):
    """
    A user belonging to an organization
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="memberships",)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="memberships",)
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["user", "organization"],
                name="unique_user_org_membership",
            )
        ]
        
    def __str__(self):
        return f"{self.user.username} @ {self.organization.slug}"