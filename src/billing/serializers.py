from rest_framework import serializers
 
from .models import Plan, OrganizationSubscription, UsageRecord

class PlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = Plan
        fields = ["code", "name", "app_limit", "monthly_request_limit", "stripe_price_id"]
        
class OrganizationSubscriptionSerializer(serializers.ModelSerializer):
    plan = PlanSerializer(read_only=True)
    
    class Meta:
        model = OrganizationSubscription
        fields = [
            "id",
            "status",
            "plan",
            "stripe_customer_id",
            "stripe_subscription_id",
            "current_period_start",
            "current_period_end",
        ]

class UsagerecordSerializer(serializers.ModelSerializer):
    class Meta:
        model = UsageRecord
        fields = ["metric", "period_start", "period_end", "quantity"]
        
class SubscriptionUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrganizationSubscription
        fields = [
            "plan",
            "status",
            "stripe_customer_id",
            "stripe_subscription_id",
            "current_period_start",
            "current_period_end",
        ]