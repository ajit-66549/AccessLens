from django.urls import path
from .views import CurrentOrgView

urlpatterns = [
    path('current/', CurrentOrgView.as_view(), name="current-org"),
]
