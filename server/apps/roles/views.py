from rest_framework import viewsets 
from apps.roles.models import Role 
from apps.roles.serializers import RoleSerializer
import os,sys
sys.path.append(os.path.abspath(os.path.join('../')))
from example import simple_auction

class RoleViewSet(viewsets.ModelViewSet):

    serializer_class = RoleSerializer
    queryset = Role.objects.all()

    def list(self, request, *args, **kwargs):
        simple_auction()
        return super().list(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)