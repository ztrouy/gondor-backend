from gondorapi.models import PatientData, User, Log
from .users import ClinicianSerializer 
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import Group
from django.shortcuts import get_object_or_404

class PatientSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "fullName"]

    def get_fullName(self,obj):
        return f"{obj.first_name} {obj.last_name}"


class PatientDataSerializer(serializers.ModelSerializer):
    clinician = serializers.SerializerMethodField()

    class Meta:
        model = PatientData
        fields = ["id", "created_timestamp", "clinician"]
    
    def get_clinician(self,obj):
        serializer = ClinicianSerializer(obj.created_by)
        return serializer.data
    
class SpecificPatientDataSerializer(serializers.ModelSerializer):
    clinician = serializers.SerializerMethodField()
    updating_clinician = serializers.SerializerMethodField()
    patient = serializers.SerializerMethodField()

    class Meta:
        model = PatientData
        fields = ["id", "patient", "appointment", "clinician", "updating_clinician", "created_timestamp", "patient_diastolic", "patient_systolic", "is_notes_shared", "clinician_notes"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["updatedClinician"] = rep.pop("updating_clinician")
        rep["createdTimestamp"] = rep.pop("created_timestamp")
        rep["patientDiastolic"] = rep.pop("patient_diastolic")
        rep["patientSystolic"] = rep.pop("patient_systolic")
        rep["isNotesShared"] = rep.pop("is_notes_shared")
        rep["clinicianNotes"] = rep.pop("clinician_notes")
        return rep
    
    def get_patient(self,obj):
        serializer = PatientSerializer(obj.patient)
        return serializer.data
    
    def get_clinician(self,obj):
        serializer = ClinicianSerializer(obj.created_by)
        return serializer.data
    
    def get_updating_clinician(self,obj):
        serializer = ClinicianSerializer(obj.updated_by)
        return serializer.data

class RecordViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="me")
    def get_my_records(self, request):
        user = request.user

        if user.groups.filter(name="Patient").exists():
            filters = Q(patient=request.user)

            before_date = request.GET.get("before")
            after_date = request.GET.get("after")

            if before_date != None:
                filters &= Q(created_timestamp__lt = before_date)

            if after_date != None:
                filters &= Q(created_timestamp__gt=after_date)

            records = PatientData.objects.filter(filters)
            serializer = PatientDataSerializer(records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Unauthorized access. Only patients can access their records"}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self,request, pk=None):
        user = request.user
        # using get_object_or_404 because when i tried patientData.objects.get it would tell me that patientData has not objects. but this works as intended.
        found_record = get_object_or_404(PatientData, id=pk)
        is_authorized_user = (
            found_record.patient == user or
            found_record.created_by == user or
            found_record.updated_by == user
        )

        if not is_authorized_user:
            return Response({"error": "Unauthorized access"}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            Log.objects.create(viewed_by=user, patient_data=found_record)
        except Exception as e :
            return Response({"error": f"Log creation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        serializer = SpecificPatientDataSerializer(found_record)
        return Response(serializer.data)
    

