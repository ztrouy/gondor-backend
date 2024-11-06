from gondorapi.models import PatientData
from gondorapi.serializers import EmbeddedSerializers
from rest_framework import serializers


class PatientDataSerializers:
    class PatientDataSerializer(serializers.ModelSerializer):
        clinician = serializers.SerializerMethodField()
        updating_clinician = serializers.SerializerMethodField()
        patient = serializers.SerializerMethodField()

        class Meta:
            model = PatientData
            fields = ["id", "patient", "appointment", "clinician", "updating_clinician", "created_timestamp", "patient_diastolic", "patient_systolic", "is_notes_shared", "clinician_notes"]

        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["updatingClinician"] = rep.pop("updating_clinician")
            rep["createdTimestamp"] = rep.pop("created_timestamp")
            rep["patientDiastolic"] = rep.pop("patient_diastolic")
            rep["patientSystolic"] = rep.pop("patient_systolic")
            rep["isNotesShared"] = rep.pop("is_notes_shared")
            rep["clinicianNotes"] = rep.pop("clinician_notes")
            return rep
        
        def get_patient(self,obj):
            serializer = EmbeddedSerializers.EmbeddedUserSimpleSerializer(obj.patient)
            return serializer.data
        
        def get_clinician(self,obj):
            serializer = EmbeddedSerializers.EmbeddedUserSimpleSerializer(obj.created_by)
            return serializer.data
        
        def get_updating_clinician(self,obj):
            serializer = EmbeddedSerializers.EmbeddedUserSimpleSerializer(obj.updated_by)
            return serializer.data


    class PatientDataSimpleSerializer(serializers.ModelSerializer):
        clinician = serializers.SerializerMethodField()

        class Meta:
            model = PatientData
            fields = ["id", "created_timestamp", "clinician"]
        
        def get_clinician(self,obj):
            serializer = EmbeddedSerializers.EmbeddedUserSimpleSerializer(obj.created_by)
            return serializer.data


    class PatientDataVitalsSerializer(serializers.ModelSerializer):
        class Meta:
            model = PatientData
            fields = ["patient_systolic", "patient_diastolic", "patient_weight_kg"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["patientSystolic"] = rep.pop("patient_systolic")
            rep["patientDiastolic"] = rep.pop("patient_diastolic")
            rep["patientWeightKg"] = rep.pop("patient_weight_kg")
            return rep