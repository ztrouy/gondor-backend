from gondorapi.models import  User
from gondorapi.serializers import EmbeddedSerializers
from django.contrib.auth.hashers import check_password
from rest_framework import serializers


class UserSerializers:
    class UserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["first_name", "last_name", "full_name", "date_of_birth", "email"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            rep["dateOfBirth"] = rep.pop("date_of_birth")
            return rep


    class UserWithAddressSerializer(serializers.ModelSerializer):
        fullName = serializers.SerializerMethodField()
        primaryAddress = serializers.SerializerMethodField()

        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "date_of_birth", "email", "primaryAddress"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            rep["dateOfBirth"] = rep.pop("date_of_birth")
            return rep
        
        def get_primaryAddress(self, obj):
            address = obj.primary_address
            if address:
                serialized_address = EmbeddedSerializers.EmbeddedAddressSerializer(address).data
                return serialized_address
            
            return None


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
        
        def validate(self, attrs):
            validation_errors = check_password(self.validated_data["old_password"], self.instance.password)
            if not validation_errors:
                raise serializers.ValidationError("Old password does not match current password.")
            return super().validate(attrs)

        def update(self, instance, validated_data):
            instance.set_password(validated_data["new_password"])
            instance.save()
            return instance