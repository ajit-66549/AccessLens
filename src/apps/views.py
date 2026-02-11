from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .models import App
from .serializers import AppSerializer
from projects.models import Project
from orgs.permissions import HasOrgMembership
from rbac.permissions import IsOrgAdminOrOwner
from audit.services import write_audit_event

# Create your views here.
class AppListCreateView(APIView):
    permission_classes = [HasOrgMembership]
    
    def get_permissions(self, request):
        if self.request.method in ["POST"]:
            return [IsOrgAdminOrOwner()]
        return [HasOrgMembership()]
    
    # get all the apps
    def get(self, request):
        qs = App.objects.filter(organization=request.org).select_related("project").order_by("-created_at")
        return Response(AppSerializer(qs, many=True).data)
    
    # create a new app
    def post(self, request):
        serializer = AppSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        project: Project = serializer.validated_data["project"]
        
        if project.organization_id != request.org.id:
            return Response({"detail": "Project does not belong to this organization."}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            app = App.objects.create(
            organization=request.org,
            **serializer.validated_data,
            )
        except IntegrityError:
            return ValidationError({"details": "App key must be unique within the project"})
        
        # Audit log
        write_audit_event(request=request, 
                          organization=request.org,
                          action="app.created",
                          target_type="App",
                          target_id=app.id,
                          meta={"key": app.key, "name": app.name, "project_id": str(app.project_id)},)
        
        return Response(AppSerializer(app).data, status=status.HTTP_201_CREATED)
    
class AppDetailView(APIView):
    permission_classes = [HasOrgMembership]
    
    def get_permissions(self):
        if self.request.method in {"PUT", "PATCH", "DELETE"}:
            return [IsOrgAdminOrOwner()]
        return [HasOrgMembership()]
    
    def get_object(self, request, app_id):
        return get_object_or_404(App, id=app_id, organization=request.org)
    
    def get(self, request, app_id):
        app = self.get_object(request, app_id)
        return Response(AppSerializer(app).data)
    
    def put(self, request, app_id):
        return self._update(request, app_id, partial=False)
    
    def patch(self, request, app_id):
        return self._update(request, app_id, partial=True)
    
    def _update(self, request, app_id, *, partial):
        app = self.get_object(request, app_id)
        serializer = AppSerializer(app, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        if "project" in serializer.validated_data:
            project = serializer.validated_data["project"]
            if project.organization_id != request.org.id:
                return Response({"details": "Project does not belong to this organization."},
                                status=status.HTTP_400_BAD_REQUEST)
        
        try:
            app = serializer.save()
        except IntegrityError:
            return ValidationError({"details": "App key must be unique within the project"})
        
        write_audit_event(
            request=request,
            organization=request.org,
            action="App.updated",
            target_type="App",
            target_id=app.id,
            meta={"key": app.key, "name": app.name, "project_id": str(app.project_id)}
        )
        return Response(AppSerializer(app).data)
    
    def delete(self, request, app_id):
        app = self.get_object(request, app_id)
        app_snap = {"key": app.key, "name": app.name, "project_id": str(app.project_id)}
        app_id = app.id
        app.delete()
        
        write_audit_event(
            request=request,
            organization=request.org,
            action="App.deleted",
            target_type="App",
            target_id=app.id,
            meta=app_snap
        )
        return Response({"details": "App Deleted"}, status=status.HTTP_204_NO_CONTENT)
    
class ProjectAppDetailView(APIView):
    permission_classes = [HasOrgMembership]
    
    def get_permissions(self, request):
        if self.request.method in ["POST"]:
            return [IsOrgAdminOrOwner()]
        return [HasOrgMembership()]
    
    # first get the project
    def get_project(self, request, project_id):
        return get_object_or_404(Project, id=project_id, organization=request.org)
    
    # get all the apps in that project
    def get(self, request, project_id):
        project = self.get_project(request, project_id)
        all_apps = App.objects.filter(organization=request.org, project=project).select_related("project").order_by("-created_at")
        return Response(AppSerializer(all_apps).data)
    
    # create new app in that project
    def post(self, request, project_id):
        project = self.get_project(request, project_id)
        serializer = AppSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        if "project" in serializer.validated_data and serializer.validated_data["project"].id != project.id:
            return Response({"details": "Project does not match the requested project."}, status=status.HTTP_400_BAD_REQUEST)
        
        app_payload = dict(serializer.validated_data)
        app_payload.pop("project", None)  # removing project does't let to client to decide which project, app belongs to
        
        try:
            app = App.objects.create(organization=request.org, project=project, **app_payload)
        except IntegrityError:
            return ValidationError({"details": "App key must be unique within the project"})
        
        write_audit_event(
            request=request,
            organization=request.org,
            action="App.created",
            target_type="App",
            target_id=app.id,
            meta={"key": app.key, "name": app.name, "project_id": str(app.project_id)},
        )
        return Response(AppSerializer(app).data, status=status.HTTP_201_CREATED)