from gondorapi.models import Address, Appointment, User
from rest_framework import serializers


class EmbeddedSerializers:
    #region Users
    class EmbeddedUserSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name", "date_of_birth", "email"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            rep["dateOfBirth"] = rep.pop("date_of_birth")
            return rep


    class EmbeddedUserSimpleSerializer(serializers.ModelSerializer):
        class Meta:
            model = User
            fields = ["id", "first_name", "last_name", "full_name"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            return rep


    #region Addresses
    class EmbeddedAddressSerializer(serializers.ModelSerializer):
        class Meta:
            model = Address
            fields = ["line1", "line2", "city", "state_code", "postal_code"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["stateCode"] = rep.pop("state_code")
            rep["postalCode"] = rep.pop("postal_code")
            return rep


    #region Appointments
    class EmbeddedAppointmentSimpleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Appointment
            fields = ["id", "scheduled_timestamp"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["scheduledTimestamp"] = rep.pop("scheduled_timestamp")
            return rep