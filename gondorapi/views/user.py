from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from gondorapi.models import User


class UserSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "fullName", "date_of_birth", "email"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        rep["dateOfBirth"] = rep.pop("date_of_birth")
        return rep

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"


class UserViewSet(viewsets.ViewSet):
    def retrieve(self, request, pk=None):
        users = User.objects.all()
        user = users.get_object_or_404(users, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)