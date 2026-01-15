from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "organization", "key", "name", "is_active", "created_at")
    search_fields = ("key", "name", "organization__slug")
    list_filter = ("is_active", "organization")
