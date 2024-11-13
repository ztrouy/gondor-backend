from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth import authenticate
from gondorapi.models import State
from gondorapi.serializers import StateSerializers


class StateViewSet(viewsets.ViewSet):
    def list(self, request):
        states = State.objects.all()
        serializer = StateSerializers.StateSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)