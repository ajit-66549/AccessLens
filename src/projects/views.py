from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Project
from .serializers import ProjectSerializer
from orgs.permissions import HasOrgMembership

from django.db import IntegrityError
from rest_framework.exceptions import ValidationError

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