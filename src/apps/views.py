from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from orgs.permissions import HasOrgMembership
from projects.models import Project
from .models import App
from .serializers import AppSerializer

from audit.services import write_audit_event

# Create your views here.
class AppListCreateView(APIView):
    permission_classes = [HasOrgMembership]
    
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
        
        app = App.objects.create(
            organization=request.org,
            **serializer.validated_data,
        )
        # Audit log
        write_audit_event(request=request, 
                          organization=request.org,
                          action="app.created",
                          target_type=" App",
                          target_id=app.id,
                          meta={"key": app.key, "name": app.name, "project_id": str(app.project_id)},)
        
        return Response(AppSerializer(app).data, status=status.HTTP_201_CREATED)