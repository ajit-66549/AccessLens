from django.urls import path
from .views import ProjectListCreateView, ProjectDetailView

urlpatterns = [
    path("", ProjectListCreateView.as_view(), name="projects"),
    path("<uuid:project_id>/", ProjectDetailView.as_view(), name="project_details"),
]
