from gondorapi.models import PatientData, User
from .user import ClinicianSerializer 
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.contrib.auth.models import Group


class PatientDataSerializer(serializers.ModelSerializer):
    clinician = serializers.SerializerMethodField()

    class Meta:
        model = PatientData
        fields = ["id", "created_timestamp", "clinician"]
    
    def get_clinician(self,obj):
        serializer = ClinicianSerializer(obj.created_by)
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
        
        return Response({"error": "Unauthorized access. Only patients can access their records"})