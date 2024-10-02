from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from gondorapi.models import User

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ["old_password", "new_password"]
    
    def to_internal_value(self, data):
        data = data.copy()
        data["old_password"] = data.pop("oldPassword")
        data["new_password"] = data.pop("newPassword")
        return super().to_internal_value(data)
    
    def update(self, instance, validated_data):
        pass

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "date_of_birth"]
    
    def to_internal_value(self, data):
        data = data.copy()
        data["first_name"] = data.pop("firstName")
        data["last_name"] = data.pop("lastName")
        data["date_of_birth"] = data.pop("dateOfBirth")
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.first_name = validated_data["first_name"]
        instance.last_name = validated_data["last_name"]
        instance.date_of_birth = validated_data["date_of_birth"]
        instance.save()
        return instance

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
    @action(detail=False, methods=["get"], url_path="me")
    def get_my_details(self, request):
        serializer = UserSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["put"], url_path="edit-account")
    def edit_account(self, request):
        serializer = UserEditSerializer(request.user, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], url_path="change-password")