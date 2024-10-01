from rest_framework import viewsets, status, serializers, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from gondorapi.models import User


class UserCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password", "first_name", "last_name", "date_of_birth"]
        extra_kwargs = {"password": {"write_only": True}}
    
    def to_internal_value(self, data):
        data = data.copy()
        data["first_name"] = data.pop("firstName")
        data["last_name"] = data.pop("lastName")
        data["date_of_birth"] = data.pop("dateOfBirth")
        return super().to_internal_value(data)
    
    def create(self, validated_data):
        user = User.objects.create_user(
            email = validated_data["email"],
            username = validated_data["email"],
            password = validated_data["password"],
            first_name = validated_data["first_name"],
            last_name = validated_data["last_name"],
            date_of_birth = validated_data["date_of_birth"]
        )
        return user


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=["post"], url_path="register")
    def register_patient(self, request):
        serializer = UserCreateSerializer(data=request.data)
        if serializer.is_valid():            
            user = serializer.save()

            patient_role = Group.objects.get(name="Patient")
            user.groups.add(patient_role)

            token, created = Token.objects.get_or_create(user=user)

            return Response({"token": token.key}, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["post"], url_path="login")
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")
        
        user = authenticate(email=email, password=password)

        if user:
            token = Token.objects.get(user=user)
            return Response({"token": token.key}, status=status.HTTP_200_OK)
        
        else:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_400_BAD_REQUEST)