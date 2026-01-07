from rest_framework import serializers
from orgs.models import Membership

class MeSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    full_name = serializers.CharField(allow_blank = True)
    orgs = serializers.ListField()
    
    def to_representation(self, instance):
        user = instance
        memberships = (Membership.objects.select_related("organization").prefetch_related("role_assignments__role").filter(user=user, is_active=True))
        
        orgs = []
        for m in memberships:
            role_keys = [ra.role.key for ra in m.role_assignments.all()]     # list of roles in the membership
            orgs.append({
                "org_id": str(m.organization.id),  # id of oraganization
                "name": m.organization.name,       # name of organization
                "slug": m.organization.slug,       # slug of organization
                "roles": role_keys,                # roles in that organization
            })
            
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "orgs": orgs,
        }