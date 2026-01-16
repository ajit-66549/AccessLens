from django.urls import path
from .views import AppListCreateView
from .views_api_keys import CreateApiKeyView 

urlpatterns = [
    path("", AppListCreateView.as_view(), name="apps"),
    path("<uuid:app_id>/keys/", CreateApiKeyView, name="app_create_key"),
]
