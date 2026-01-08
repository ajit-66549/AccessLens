from django.urls import path
from .views import WhoAmIScopedView

urlpatterns = [
    path('whoamI/', WhoAmIScopedView.as_view(), name="rbac-whoami"),
]
