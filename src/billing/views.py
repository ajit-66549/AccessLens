from datetime import date

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView

from orgs.permissions import HasOrgMembership
from rbac.permissions import IsOrgAdminOrOwner
from .services import get_or_create_org_subscription, record_usage
from .models import UsageRecord
from .serializers import (
    OrganizationSubscriptionSerializer,
    SubscriptionUpdateSerializer,
    UsagerecordSerializer
)

# retrieve the subscription that org has and its usage record 
class BillingCurrentView(APIView):
    permission_classes = [HasOrgMembership]
    
    def ger(self, request):
        subscription = get_or_create_org_subscription(request.org)
        usage = UsageRecord.objects.filter(
            organization=request.org,
            period_start__month=date.today().month,
            period_start__year=date.today().year,
        ).order_by("metric")
        
        return Response(
            {"subscription": OrganizationSubscriptionSerializer(subscription),
             "usage": UsagerecordSerializer(usage, many=True).data}     
        )

# change the plan
class BillingSubscriptionView(APIView):
    permission_classes = [IsOrgAdminOrOwner]
    
    def patch(self, request):
        subscription = get_or_create_org_subscription(request.org)
        serializer = SubscriptionUpdateSerializer(subscription, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(OrganizationSubscriptionSerializer(subscription).data)
    
class UsageTrackView(APIView):
    permission_classes = [HasOrgMembership]
    
    def post(self, request):
        metric = request.data.get("metric")
        quantity = int(request.data.get("quantity", 1))  # if client doen't send quantity, set to 1
        if metric not in {"api_requests", "apps"}:
            return Response({"detail": "Unsupported metric."}, status=status.HTTP_400_BAD_REQUEST)
        # if quantity <=0
        if quantity < 1:
            return Response({"detail": "Quantity must be >= 1"}, status=status.HTTP_400_BAD_REQUEST)
        
        # update in database
        usage = record_usage(request.org, metric, quantity)
        return Response(UsagerecordSerializer(usage).data, status=status.HTTP_201_CREATED)