from rest_framework import serializers
from gondorapi.models import User
from gondorapi.serializers import EmbeddedSerializers


class PatientSerializers:
    class PatientSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "is_active"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            rep["isActive"] = rep.pop("is_active")
            return rep
        

    class PatientWithAppointmentSerializer(serializers.ModelSerializer):
        appointment = serializers.SerializerMethodField()
        
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "appointment"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            return rep

        def get_appointment(self, obj):
            serializer = EmbeddedSerializers.EmbeddedAppointmentSimpleSerializer(obj.next_appointment, read_only=True)
            return serializer.data
        

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
        appointment = serializers.SerializerMethodField()

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

        def get_appointment(self, obj):
            if obj.appointment:
                serializer = EmbeddedSerializers.EmbeddedAppointmentSimpleSerializer(obj.appointment, read_only=True)
                return serializer.data
            return None