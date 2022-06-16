from rest_framework import serializers
from apps.assetManager.models import Asset

class AssetSerializer(serializers.ModelSerializer):

    class Meta:
        model = Asset
        read_only_fields = (
            "id",
            "created_at",
            "created_by",
        )
        fields = (
            "id",
            "created_at",
            "created_by",
            "content"
        )