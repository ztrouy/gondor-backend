from gondorapi.models import User
from rest_framework import serializers


class AuthSerializers:
    class UserAuthSerializer(serializers.ModelSerializer):
        roles = serializers.SerializerMethodField()
        
        class Meta:
            model = User
            fields = ["roles"]

        def get_roles(self, obj):
            return [group.name for group in obj.groups.all()]