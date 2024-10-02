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

    # def to_internal_value(self, data):
    #     data = data.copy()
    #     data["first_name"] = data.pop("firstName")
    #     return super().to_internal_value(data)
    
    # def create(self, validated_data):
    #     user = User.objects.create_user(
    #         email = validated_data["email"],
    #         username = validated_data["email"],
    #         password = validated_data["password"],
    #         first_name = validated_data["first_name"],
    #         last_name = validated_data["last_name"],
    #         date_of_birth = validated_data["date_of_birth"]
    #     )
    #     return user


class StateViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    
    def list(self, request):
        states = State.objects.all()
        serializer = StateSerializer(states, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # @action(detail=False, methods=["post"], url_path="register")
    # def register_patient(self, request):
    #     serializer = UserCreateSerializer(data=request.data)
    #     if serializer.is_valid():            
    #         user = serializer.save()

    #         patient_role = Group.objects.get(name="Patient")
    #         user.groups.add(patient_role)

    #         token, created = Token.objects.get_or_create(user=user)

    #         return Response({"token": token.key}, status=status.HTTP_201_CREATED)

    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    # @action(detail=False, methods=["post"], url_path="login")
    # def login(self, request):
    #     email = request.data.get("email")
    #     password = request.data.get("password")
        
    #     user = authenticate(email=email, password=password)

    #     if user:
    #         token = Token.objects.get(user=user)
    #         return Response({"token": token.key}, status=status.HTTP_200_OK)
        
    #     else:
    #         return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)