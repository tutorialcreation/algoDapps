from rest_framework import serializers
from apps.assetManager.models import Nft

class AssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Nft
        fields = '__all__'