from django.urls import path
from .views import BillingCurrentView, BillingSubscriptionView, UsageTrackView

urlpatterns = [
    path("current/", BillingCurrentView.as_view(), name="current-billing"),
    path("subscription/", BillingSubscriptionView.as_view(), name="subscription-billing"),
    path("usage/track/", UsageTrackView.as_view(), name="track0-usage"),
]
