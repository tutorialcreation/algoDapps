from rest_framework import viewsets 
from apps.assetManager.models import Asset 
from apps.assetManager.serializers import AssetSerializer
import os,sys
sys.path.append(os.path.abspath(os.path.join('../')))
from example import simple_auction

class AssetViewSet(viewsets.ModelViewSet):

    serializer_class = AssetSerializer
    queryset = Asset.objects.all()


    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(created_by=self.request.user)