from gondorapi.models import PatientData
from gondorapi.serializers import EmbeddedSerializers
from rest_framework import serializers
import datetime


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
    

    class PatientDataEditSerializer(serializers.ModelSerializer):
        class Meta:
            model = PatientData
            fields = ["patient_systolic", "patient_diastolic", "patient_weight_kg", "clinician_notes"]
        
        def to_internal_value(self, data):
            data = data.copy()
            data["patient_systolic"] = data.pop("patientSystolic")
            data["patient_diastolic"] = data.pop("patientDiastolic")
            data["patient_weight_kg"] = data.pop("patientWeightKg")
            data["clinician_notes"] = data.pop("clinicianNotes")
            return super().to_internal_value(data)
        
        def update(self, instance, validated_data):
            instance.patient_systolic = validated_data["patient_systolic"]
            instance.patient_diastolic = validated_data["patient_diastolic"]
            instance.patient_weight_kg = validated_data["patient_weight_kg"]
            instance.clinician_notes = validated_data["clinician_notes"]
            instance.updated_by = self.context["request"].user
            instance.save()
            return instance

        
    class PatientDataCreateSerializer(serializers.ModelSerializer):
        class Meta:
            model = PatientData
            fields = ["patient", "appointment", "patient_systolic", "patient_diastolic", "patient_weight_kg", "clinician_notes", "is_notes_shared"]

        def to_internal_value(self, data):
            data = data.copy()
            data["patient_systolic"] = data.pop("patientSystolic")
            data["patient_diastolic"] = data.pop("patientDiastolic")
            data["patient_weight_kg"] = data.pop("patientWeightKg")
            data["clinician_notes"] = data.pop("clinicianNotes")
            data["is_notes_shared"] = data.pop("isNotesShared")
            return super().to_internal_value(data)
        
        def create(self, validated_data):
            patient_data = PatientData.objects.create(
                patient = validated_data["patient"],
                appointment = validated_data["appointment"],
                created_by = self.context["request"].user,
                patient_systolic = validated_data["patient_systolic"],
                patient_diastolic = validated_data["patient_diastolic"],
                patient_weight_kg = validated_data["patient_weight_kg"],
                clinician_notes = validated_data["clinician_notes"],
                is_notes_shared = validated_data["is_notes_shared"]
            )
            return patient_data