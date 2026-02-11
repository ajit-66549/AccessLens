from django.urls import path
from .views import AppListCreateView, AppDetailView
from .views_api_keys import ApiKeyListCreateView, ApiKeyRevokeView, ApiKeyRotateView, ApiKeyPingView

urlpatterns = [
    path("", AppListCreateView.as_view(), name="apps"),
    path("<uuid:app_id>/keys/", ApiKeyListCreateView.as_view(), name="list-create-key"),
    path("<uuid:app_id>/keys/<uuid:key_id>/revoke/", ApiKeyRevokeView.as_view(), name="revoke-apikey"),
    path("<uuid:app_id>/keys/<uuid:key_id>/rotate/", ApiKeyRotateView.as_view(), name="rotate-apikey"),
    path("ping/", ApiKeyPingView.as_view(), name="api_view"),
    path("<uuid:app_id>/", AppDetailView.as_view(), name="app_details"),
]
