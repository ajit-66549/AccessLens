from django.db import IntegrityError
from django.shortcuts import get_object_or_404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import ValidationError

from .models import Project
from .serializers import ProjectSerializer
from orgs.permissions import HasOrgMembership
from audit.services import write_audit_event

# Create your views here.
class ProjectListCreateView(APIView):
    # verify the user is the member of that organization, if yes then organization and membership are attached on request
    permission_classes = [HasOrgMembership]
    
    # validated user can get all the project of that organization
    def get(self, request):
        qs = Project.objects.filter(organization=request.org).order_by("-created_at")
        return Response(ProjectSerializer(qs, many=True).data)
    
    # validated user can create a new project in that organization
    def post(self, request):
        serializer = ProjectSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            project = Project.objects.create(organization=request.org, **serializer.validated_data,)
            # Audit log
            write_audit_event(
                request=request,
                organization=request.org,
                action = "project.created",
                target_type = "Project",
                target_id = project.id,
                meta = {"key": project.key, "name": project.name},
            )
            return Response(ProjectSerializer(project).data, status=status.HTTP_201_CREATED)
        except IntegrityError:
            raise ValidationError({"key": "Project key must be unique within the organization"})
        
class ProjectDetailView(APIView):
    # be the member of org to access the project
    permission_classes = [HasOrgMembership]
    
    # get the project whose id is project_id and belongs to request.org
    def get_object(self, request, project_id):
        return get_object_or_404(Project, id = project_id, organization = request.org)
    
    # fetch the project whose id is project_id
    def get(self, request, project_id):
        project = self.get_object(request, project_id)
        return Response(ProjectSerializer(project).data)
    
    # updates the whole project 
    def put(self, request, project_id):
        return self._update(request, project_id, partial=False)
    
    # updates the partial project
    def patch(self, request, project_id):
        return self._update(request, project_id, partial=True)
    
    def _update(self, request, project_id, *, partial):
        project = self.get_object(request, project_id)
        serializer = ProjectSerializer(project, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        try:
            project = serializer.save()
        except IntegrityError:
            return ValidationError({"details": "Project key must be unique within the organization"})
        
        # audit the event
        write_audit_event(
            request=request, 
            organization=request.org,
            action="Project.updated",
            target_type="Project",
            target_id=project.id,
            meta = {"key": project.key, "name": project.name},
        )
        return Response(ProjectSerializer(project).data)
    
    def delete(self, request, project_id):
        project = self.get_object(request, project_id)
        project_snap = {"key": project.key, "name": project.name},
        project_id = project.id
        project.delete()
        
        write_audit_event(
            request=request,
            organization=request.org,
            action="Project.deleted",
            target_type="Project",
            target_id=project_id,
            meta = project_snap,
        )
        return Response({"details": "Project Deleted"}, status=status.HTTP_204_NO_CONTENT)