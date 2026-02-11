# Org->Project->App
import re
import uuid
import secrets
import string
import hashlib

from django.conf import settings
from django.db import models

from orgs.models import Organization
from projects.models import Project
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
    
    # creates a compiled regex pattern
    KEY_PREFIX = "alx";
    KEY_PATTERN = re.compile("^alx_([A-Za-z0-9]{32})_([A-Fa-f0-9]{8})$")
    
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
 
    @classmethod
    def _checksum_for_body(cls, body: str) -> str:
        return hashlib.sha256(body.encode("utf-8")).hexdigest()
    
    @classmethod
    def _validate_key_format(cls, raw_key: str) -> bool:
        match = cls.KEY_PATTERN.match(raw_key or "")     # format check (Does it look right?)
        if not match:
            return False
        body, checksum = match.groups()
        return secrets.compare_digest(checksum.lower(), cls._checksum_for_body(body).lower())    # Is it truly valid?
    
    @classmethod
    def generate_api_key(cls) -> str:
        """Generate prefixed API key with checksum."""
        alphabet = string.ascii_letters + string.digits
        body = "".join(secrets.choice(alphabet) for _ in range(32))
        checksum = cls._checksum_for_body(body)
        return f"{cls.KEY_PREFIX}_{body}_{checksum}"

    @classmethod
    def hash_key(cls, raw_key: str) -> str:
        """Hash API key after validating format and checksum."""
        if not cls.validate_key_format(raw_key):
            raise ValueError("Invalid API key format or checksum.")
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()