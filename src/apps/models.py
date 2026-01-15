# Org->Project->App
import uuid
from django.db import models
from orgs.models import Organization
from projects.models import Project

# Create your models here.
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