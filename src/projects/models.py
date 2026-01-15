import uuid
from django.db import models
from orgs.models import Organization


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name="projects",
    )

    key = models.SlugField(max_length=50)  # short unique id inside an org (e.g. "webapp", "mobile")
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)

    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "key"],
                name="unique_project_key_per_org",
            )
        ]

    def __str__(self):
        return f"{self.organization.slug}:{self.key}"
