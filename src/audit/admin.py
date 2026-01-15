from django.contrib import admin
from .models import AuditEvent

# Register your models here.
@admin.register(AuditEvent)

class AuditEventAdmin(admin.ModelAdmin):
    list_display = ("created_at", "organization", "actor", "action", "target_type", "target_id")
    list_filter = ("organization", "action", "target_type")
    search_fields = ("action", "target_type", "target_id", "organization__slug", "actor__username")
    ordering = ("-created_at",)