from rest_framework import serializers
from .models import Project

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = ["id", "key", "name", "description", "is_active", "created_at", "updated_at"]
        read_only_fields = ["id", "is_active", "created_at", "updated_at"]
