from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import authenticate
from django.contrib.auth.models import Group
from gondorapi.models import User
from gondorapi.serializers import AuthSerializers, UserSerializers


class AuthViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    
    @action(detail=False, methods=["post"], url_path="register")
    def register_patient(self, request):
        serializer = UserSerializers.UserCreateSerializer(data=request.data)
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
        
    @action(detail=False, methods=["post"], url_path="me")
    def authenticate_user(self, request):
        token_key = request.data.get("token")

        try:
            token = Token.objects.get(key=token_key)
            user = User.objects.get(id=token.user_id)
            serializer = AuthSerializers.UserAuthSerializer(user, context={"request": request})
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        except Token.DoesNotExist:
            return Response({"error": "Invalid credentials"}, status=status.HTTP_401_UNAUTHORIZED)