from django.urls import path
from .views import AppListCreateView, AppDetailView
from .views_api_keys import CreateApiKeyView, ApiKeyPingView

urlpatterns = [
    path("", AppListCreateView.as_view(), name="apps"),
    path("<uuid:app_id>/keys/", CreateApiKeyView.as_view(), name="app_create_key"),
    path("ping/", ApiKeyPingView.as_view(), name="api_view"),
    path("<uuid:app_id>/", AppDetailView.as_view(), name="app_details"),
]
