# Org->Project->App
import uuid
from django.db import models
from orgs.models import Organization
from projects.models import Project

import secrets
import hashlib

from django.conf import settings

# Create your models here.

# App model
class App(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="apps",)
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="apps",)
    
    key = models.SlugField(max_length=50)
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["project", "key"],
                name="unique_app_key_per_project",
            )
        ]
        
    def __str__(self):
                 # Organization: Project: App
        return f"{self.organization.slug}: {self.project.key}: {self.key}"

# Apikey model
class Apikey(models.Model):
    """
    Stores a hashed API key for an App.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    app = models.ForeignKey("apps.App", on_delete=models.CASCADE, related_name="api_keys")
    key_hash = models.CharField(max_length=64, unique=True)
    name = models.CharField(max_length=120, blank=True)
    
    is_active = models.BooleanField(default=True)
    
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL,
                                   on_delete=models.CASCADE,
                                   null=True,
                                   blank=True,
                                   related_name="created_api_keys")
    
    created_at = models.DateTimeField(auto_now_add=True)
    revoked_at = models.DateTimeField(null=True, blank=True)
    
    def __str__(self):
        return f"{self.app} - {self.name or 'api-key'}"
    
    @staticmethod
    def generate_api_key() -> str:
        """
        Generate a random api key to give to user/client once
        """
        return secrets.token_urlsafe(32)  # generates string with 32 bytes of randomness
    
    @staticmethod
    def hash_key(raw_key: str) -> str:
        """
        Hash the raw api key to store or compare safely
        Convert the string (raw api_key) into bytes, hash that bytes, and convert back to string
        """
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()