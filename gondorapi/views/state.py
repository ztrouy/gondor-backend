from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from gondorapi.models import State


class StateSerializer(serializers.ModelSerializer):
    class Meta:
        model = State
        fields = ["state_code", "name"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["stateCode"] = rep.pop("state_code")
        return rep


class StateViewSet(viewsets.ViewSet):
    
    def list(self, request):
        states = State.objects.all()
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)