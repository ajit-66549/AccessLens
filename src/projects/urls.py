from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView
from apps.views import ProjectAppDetailView

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="projects"),
    path("<uuid:project_id>/", ProjectDetailView.as_view(), name="project_details"),
    path("<uuid:project_id>/apps/", ProjectAppDetailView.as_view(), name="project_apps"),
]
