from rest_framework import viewsets, status, serializers, permissions
from gondorapi.models import Appointment, User
import datetime
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q

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
        return f"{obj.first_name} {obj.last_name}"

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
        return obj.is_checked_in and (datetime.datetime.now(obj.scheduled_timestamp.tzinfo).minute - obj.scheduled_timestamp.minute) > 30

class AppointmentViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="me")
    def get_patient_appointments(self, request):
        q=Q(patient=request.user)

        before_date = request.GET.get("before")
        after_date = request.GET.get("after")
        clinician_id = request.GET.get("clinician")
        is_pending = None
        match(request.GET.get("pending")):
            case "true" | "True":
                is_pending = True
            case "false" | "False":
                is_pending = False
            case _:
                is_pending = None

        if after_date != None:
            q &= Q(scheduled_timestamp__gt=after_date)
        if before_date != None:
            q &= Q(scheduled_timestamp__lt=before_date)
        if clinician_id != None:
            q &= Q(clinician__id=clinician_id)
        if is_pending == True:
            q &= Q(approver__isnull=is_pending) & Q(is_approved=False)
        elif is_pending == False:
            q &= Q(approver__isnull=False) | Q(is_approved=True)

        appointments = Appointment.objects.filter(q)
        serializer = PatientAppointmentSerializer(appointments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def retrieve(self,request, pk=None):
        user = request.user
        is_receptionist = user.groups.filter(name="Receptionist").exists()
        is_clinician = user.groups.filter(name="Clinician").exists()
        found_appointment = Appointment.objects.get(pk=pk)
        is_authorized_user = (
            found_appointment.patient == user or
            is_clinician or
            is_receptionist
        )

        if not is_authorized_user:
            return Response({"error": "You are not authorized"}, status=status.HTTP_403_FORBIDDEN)
        serializer = PatientAppointmentSerializer(found_appointment)
        return Response(serializer.data)
