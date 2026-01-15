from django.urls import path
from .views import AuditListView

urlpatterns = [
    path("", AuditListView.as_view(), name="audit-list"),
]
