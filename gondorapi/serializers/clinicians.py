from gondorapi.models import PatientClinician, User
from rest_framework import serializers


class ClinicianSerializers:
    class ClinicianSerializer(serializers.ModelSerializer):
        class Meta:
            model= User
            fields = ["first_name", "last_name", "full_name", "id"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            return rep


    class ClinicianWithIsProviderSerializer(serializers.ModelSerializer):
        isProvider = serializers.SerializerMethodField()

        class Meta:
            model = User
            fields = ["first_name", "last_name", "full_name", "id", "isProvider"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["firstName"] = rep.pop("first_name")
            rep["lastName"] = rep.pop("last_name")
            rep["fullName"] = rep.pop("full_name")
            return rep

        def get_isProvider(self,obj):
            patient = self.context.get('patient')
            return PatientClinician.objects.filter(patient=patient, clinician=obj).exists()