from gondorapi.models import User
from gondorapi.serializers import EmbeddedSerializers
from rest_framework import serializers


class PatientSerializers:
    class PatientSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "fullName", "is_active"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["isActive"] = rep.pop("is_active")
            return rep
        

    class PatientWithAppointmentSerializer(serializers.ModelSerializer):
        appointment = serializers.DateTimeField()
        
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "appointment"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            return rep
        

    class PatientWithDateOfBirthSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "date_of_birth"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            rep["dateOfBirth"] = rep.pop("date_of_birth")
            return rep
        

    class PatientWithAppointmentAndDateOfBirthSerializer(serializers.ModelSerializer):
        appointment = EmbeddedSerializers.EmbeddedAppointmentSimpleSerializer(read_only=True)

        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "date_of_birth", "appointment"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            rep["dateOfBirth"] = rep.pop("date_of_birth")
            return rep