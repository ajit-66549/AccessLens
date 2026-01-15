from rest_framework import serializers
from .models import App


class AppSerializer(serializers.ModelSerializer):
    class Meta:
        model = App
        fields = ["id", "project", "key", "name", "description", "is_active", "created_at"]
        read_only_fields = ["id", "created_at"]
