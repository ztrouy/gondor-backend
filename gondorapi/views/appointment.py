from rest_framework import viewsets, status, serializers, permissions
from gondorapi.models import Appointment
import datetime

class PatientAppointmentSerializer(serializers.ModelSerializer):
    clinicianName = serializers.CharField()
    approvalStatus = serializers.BooleanField(null=True)
    completedStatus = serializers.BooleanField()

    class Meta:
        model = Appointment
        fields = ["scheduled_timestamp", "clinician_name", "approval_status", "completed_status"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["scheduledTimestamp"] = rep.pop("scheduled_timestamp")
        rep["clinicianName"] = rep.pop("clinician_name")
        rep["approvalStatus"] = rep.pop("approval_status")
        rep["completedStatus"] = rep.pop("completed_status")
        return rep

    def get_clinicianName(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def get_approvalStatus(self, obj):
        return None if obj.approver == None and not obj.is_approved else obj.is_approved

    def get_completedStatus(self, obj):
        return obj.is_completed and obj.is_checked_in and (datetime.datetime.now() - obj.scheduled_timestamp).minutes > 30

