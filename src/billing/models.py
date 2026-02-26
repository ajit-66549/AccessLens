import uuid
from datetime import date
from django.db import models

from orgs.models import Organization

# Plan Model
class Plan(models.Model):
    code = models.SlugField(max_length=50, unique=True)
    name = models.CharField(max_length=120)
    stripe_price_id = models.CharField(max_length=120, blank=True)
    app_limit = models.PositiveIntegerField(default=1)
    monthly_request_limit = models.PositiveIntegerField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.code
    
# Model for Organization Subscription (Which org bought which plan)
class OrganizationSubscription(models.Model):
    STATUS_CHOICES = [
        ("trialing", "Trialing"),
        ("active", "Active"),
        ("past_due", "Past due"),
        ("canceled", "Canceled"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.OneToOneField(Organization, on_delete=models.CASCADE, related_name="subscription")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscription")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="active")
    
    stripe_customer_id = models.CharField(max_length=120, blank=True)
    stripe_subscription_id = models.CharField(max_length=120, blank=True)
    
    current_period_start = models.DateField(default=date.today)
    current_period_end = models.DateField(default=date.today)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.organization.slug} -> {self.plan.code}"
    
# model for Usage record of Plan (How much on org consumed)
class UsageRecord(models.Model):
    METRIC_CHOICES = [
        ("api_requests", "API requests"),
        ("apps", "Apps"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name="usage_records")
    metric = models.CharField(max_length=40, choices=METRIC_CHOICES)
    period_start = models.DateField()
    period_end = models.DateField()
    quantity = models.PositiveIntegerField(default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["organization", "metric", "period_start", "period_end"],
                name="unique_usage_per_org_metric_period",
            )
        ]
    
    def __str__(self):
        return f"{self.organization.slug}: {self.metric}: {self.period_start}"