from rest_framework import serializers
from .models import AuditEvent

class AuditEventSerialzer(serializers.ModelSerializer):
    actor = serializers.SerializerMethodField()
    
    class Meta:
        model = AuditEvent
        fields = ["id", "action", "target_type", "target_id", "actor", "meta", "created_at"]
        
    def get_actor(self, obj):
        return obj.actor.username if obj.actor else None