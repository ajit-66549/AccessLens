from rest_framework import serializers

# defining the response format
class CurrentOrgSerializer(serializers.Serializer):
    org_id = serializers.UUIDField()
    name = serializers.CharField()
    slug = serializers.CharField()
    
    membership_id= serializers.UUIDField()
    is_active = serializers.BooleanField()