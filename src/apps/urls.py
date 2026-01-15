from django.urls import path
from .views import AppListCreateView

urlpatterns = [
    path("", AppListCreateView.as_view(), name="apps"),
]
