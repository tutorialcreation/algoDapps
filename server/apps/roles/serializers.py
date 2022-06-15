from rest_framework import serializers
from apps.roles.models import Role

class RoleSerializer(serializers.ModelSerializer):

    class Meta:
        model = Role
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