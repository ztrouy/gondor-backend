from rest_framework import viewsets, status, serializers, permissions
from gondorapi.models import Appointment
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response

class PatientAppointmentSerializer(serializers.ModelSerializer):
    clinicianName = serializers.SerializerMethodField()
    approvalStatus = serializers.SerializerMethodField()
    completedStatus = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ["scheduled_timestamp", "clinicianName", "approvalStatus", "completedStatus"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["scheduledTimestamp"] = rep.pop("scheduled_timestamp")
        return rep

    def get_clinicianName(self, obj):
        return f"{obj.clinician.first_name} {obj.clinician.last_name}"
    
    def get_approvalStatus(self, obj):
        return None if obj.approver == None and not obj.is_approved else obj.is_approved

    def get_completedStatus(self, obj):
        return obj.is_approved and obj.is_checked_in and (datetime.datetime.now() - obj.scheduledTimestamp).minutes > 30

class AppointmentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="my")
    def get_patient_appointments(self, request):
        todays_date = datetime.date.today() 
        after_date = request.GET.get("afterDate") if request.GET.get("afterDate") != None else "0001-01-01"
        before_date = request.GET.get("beforeDate") if request.GET.get("beforeDate") != None else datetime.date(todays_date.year + 1, todays_date.month, todays_date.day).strftime("%Y-%m-%d")
        clinician_filter = request.GET.get("clinicianName") if request.GET.get("clinicianName") != None else ""
        appointments = Appointment.objects.filter(patient=request.user, scheduled_timestamp__range=[after_date, before_date], clinician__last_name__icontains=clinician_filter)
        serializer = PatientAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)