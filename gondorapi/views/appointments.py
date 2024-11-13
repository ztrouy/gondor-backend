from rest_framework import viewsets, status
from gondorapi.models import Appointment
from gondorapi.serializers import AppointmentSerializers
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from django.utils import timezone


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
        serializer = AppointmentSerializers.AppointmentSerializer(appointments, many=True)
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
        
        serializer = AppointmentSerializers.AppointmentSerializer(found_appointment)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="next")
    def get_next_appointment(self,request):
        user = request.user
        now = timezone.now()
        next_appointment = None
        serializer = None

        is_clinician = user.groups.filter(name="Clinician").exists()
        is_patient = user.groups.filter(name="Patient").exists()

        is_authorized_user = (
            is_clinician or
            is_patient
        )
        
        if not is_authorized_user:
            return Response({"Message": "Unauthorized user"}, status=status.HTTP_403_FORBIDDEN)

        if is_clinician:
            next_appointment=(
                Appointment.objects.filter(clinician=user, scheduled_timestamp__gt=now, is_approved=True)
                .order_by('scheduled_timestamp')
                .first()
            )
            serializer = AppointmentSerializers.AppointmentSimpleWithPatientSerializer(next_appointment)
        
        elif is_patient:
            next_appointment=(
                Appointment.objects.filter(patient=user, scheduled_timestamp__gt=now, is_approved=True)
                .order_by('scheduled_timestamp')
                .first()
            )
            
            serializer = AppointmentSerializers.AppointmentSimpleWithClinician(next_appointment)
             
        if not next_appointment:
            return Response({"Message": "No upcoming appointments found."}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.data, status=status.HTTP_200_OK)