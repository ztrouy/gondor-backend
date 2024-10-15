from rest_framework import viewsets, status, serializers, permissions
from gondorapi.models import Appointment, User
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response

class PatientAppointmentClinicianSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id", "first_name", "last_name", "fullName"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        return rep

    def get_fullName(self, obj):
        return f"{obj.clinician.first_name} {obj.clinician.last_name}"

class PatientAppointmentSerializer(serializers.ModelSerializer):
    clinician = PatientAppointmentClinicianSerializer(read_only = True)
    isPending = serializers.SerializerMethodField()
    isCompleted = serializers.SerializerMethodField()

    class Meta:
        model = Appointment
        fields = ["id", "scheduled_timestamp", "clinician", "isPending", "is_approved", "isCompleted"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["scheduledDate"] = rep.pop("scheduled_timestamp")
        rep["isApproved"] = rep.pop("is_approved")
        return rep

    def get_isPending(self, obj):
        return obj.approver == None and obj.is_approved == False

    def get_isCompleted(self, obj):
        return obj.is_checked_in and (datetime.datetime.now() - obj.scheduledTimestamp).minutes > 30



class AppointmentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="my")
    def get_patient_appointments(self, request):
        # todays_date = datetime.date.today() 
        # after_date = request.GET.get("after") if request.GET.get("after") != None else "0001-01-01"
        # before_date = request.GET.get("before") if request.GET.get("before") != None else datetime.date(todays_date.year + 1, todays_date.month, todays_date.day).strftime("%Y-%m-%d")
        # clinician_filter = request.GET.get("clinicianId") if request.GET.get("clinicianName") != None else ""
        # appointments = Appointment.objects.filter(patient=request.user, scheduled_timestamp__range=[after_date, before_date], clinician__last_name__icontains=clinician_filter)
        # serializer = PatientAppointmentSerializer(appointments, many=True)
        #return Response(serializer.data, status=status.HTTP_200_OK)

        return