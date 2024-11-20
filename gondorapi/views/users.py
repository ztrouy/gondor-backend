from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from gondorapi.models import User, PatientClinician, PatientData, Log
from gondorapi.serializers import UserSerializers, PatientSerializers, ClinicianSerializers, PatientDataSerializers, AppointmentSerializers, AddressSerializers
from django.contrib.auth.models import Group
from django.db.models import Q, Value, CharField
from django.db.models.functions import Concat
from django.utils import timezone


class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="me")
    def get_my_details(self, request):
        serializer = UserSerializers.UserWithAddressSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["put"], url_path="edit-account")
    def edit_account(self, request):
        serializer = UserSerializers.UserEditSerializer(request.user, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], url_path="change-password")
    def change_password(self, request):
        serializer = UserSerializers.ChangePasswordSerializer(request.user, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"], url_path="clinicians")
    def get_all_clinicians(self,request):
        user = request.user

        clinician_group = Group.objects.get(name="Clinician")
        clinicians = User.objects.filter(groups=clinician_group)
         
        is_active_search = self.request.query_params.get("active", None)
        if is_active_search != None:
           clinicians =  clinicians.filter(
                Q(is_active=is_active_search)
            )

        if user.groups.filter(name__in=["Clinician", "Receptionist"]).exists():
            serializer = ClinicianSerializers.ClinicianSerializer(clinicians, many=True)
            return Response(serializer.data)
        
        elif user.groups.filter(name="Patient").exists():
            assigned_clinicians = PatientClinician.objects.filter(patient=user).values_list("clinician_id", flat= True)
            serializer = ClinicianSerializers.ClinicianWithIsProviderSerializer(clinicians, many= True, context={"patient": user, "assigned_clinicians": assigned_clinicians})
            return Response(serializer.data)
        
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["get"], url_path="patient")
    def get_patient_details(self,request,pk=None):
        user = request.user

        if user.groups.filter(name__in=["Clinician", "Receptionist", "Administrator"]).exists():
            patient = User.objects.get(pk=pk)

            if not patient.is_active:
                if user.groups.filter(name__in=["Administrator"]).exists():
                    serializer = PatientSerializers.PatientSerializer(patient)
                    return Response(serializer.data)
                
                elif user.groups.filter(name__in=["Clinician", "Receptionist"]).exists():
                    return Response({"detail": "No active Patient with that Id."},status=status.HTTP_404_NOT_FOUND)
        
            serializer = PatientSerializers.PatientSerializer(patient)
            return Response(serializer.data)
        
        return Response({"detail": "You do not have permission to access this data."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=True, methods=["get"], url_path="records/last")
    def get_recent_record(self, request, pk = None):
        requester = request.user
        is_clinician = requester.groups.filter(name="Clinician").exists()
        if not is_clinician:
            return Response("You are not a Clinician", status=status.HTTP_403_FORBIDDEN)

        patient = User.objects.get(pk=pk)
        is_patient = patient.groups.filter(name="Patient").exists()
        if not is_patient:
            return Response("Requested User is not a Patient", status=status.HTTP_400_BAD_REQUEST)

        is_provider = PatientClinician.objects.filter(patient=patient, clinician=requester).exists()
        if not is_provider:
            return Response("You are not a provider for this Patient", status=status.HTTP_403_FORBIDDEN)

        try:
            recent_record = patient.personal_patient_data.latest("created_timestamp")
        
        except PatientData.DoesNotExist:
            return Response("No Medical Records exist", status=status.HTTP_404_NOT_FOUND)
        
        serializer = PatientDataSerializers.PatientDataVitalsSerializer(recent_record)
        return Response(serializer.data)
    
    @action(detail=False, methods=["get"], url_path="patients")
    def get_all_active_patients(self, request):
        user = request.user
        
        is_authorized = user.groups.filter(name__in=["Clinician", "Receptionist"]).exists()
        if not is_authorized:
            return Response("You are not authorized to see this data.", status=status.HTTP_403_FORBIDDEN)
        
        patient_group = Group.objects.get(name="Patient")
        patients = User.objects.filter(groups=patient_group, is_active=True).order_by("first_name", "last_name")

        search_name_text = self.request.query_params.get("name", None)
        is_requesting_appointment = self.request.query_params.get("appointment", None) == "true"

        if search_name_text:
            patients = patients.annotate(
                full_name = Concat("first_name", Value(" "), "last_name", output_field=CharField())
            ).filter(
                Q(full_name__icontains=search_name_text)
            )

        if is_requesting_appointment:
            for patient in patients:
                next_appointment = patient.appointments.filter(
                    is_approved = True,
                    scheduled_timestamp__gt=timezone.now()
                ).order_by("scheduled_timestamp").first()
                patient.appointment = next_appointment
            
            serializer = PatientSerializers.PatientWithAppointmentAndDateOfBirthSerializer(patients, many=True)
            return Response(serializer.data)
        
        else:
            serializer = PatientSerializers.PatientWithDateOfBirthSerializer(patients, many=True)
            return Response(serializer.data)

    @action(detail=True, methods=["get"], url_path="records")
    def get_records_of_specific_patient(self,request, pk=None):
        user = request.user
        is_authorized = user.groups.filter(name__in=["Administrator", "Clinician"]).exists()
        if not is_authorized:
            return Response("You are not authorized to see this data", status=status.HTTP_403_FORBIDDEN)

        patient = User.objects.get(pk=pk)
        filters = Q(patient=patient)
        
        clinician_id = request.GET.get("clinician")
        before_date = request.GET.get("before")
        after_date = request.GET.get("after")

        if before_date != None:
            filters &= Q(created_timestamp__lt = before_date)

        if after_date != None:
            filters &= Q(created_timestamp__gt=after_date)
        
        if clinician_id != None:
            clinician = User.objects.get(pk=clinician_id)
            filters &=Q(created_by = clinician)

        found_records = PatientData.objects.filter(filters)
        serializer = PatientSerializers.PatientDataSerializer(found_records, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="appointments")
    def get_patients_appointments(self, request, pk=None):
        requester = request.user

        is_allowed = requester.groups.filter(name__in=["Clinician", "Receptionist"]).exists()
        if not is_allowed:
            return Response("You are not authorized to request this user data", status=status.HTTP_403_FORBIDDEN)

        try:
            patient = User.objects.get(pk=pk)
            is_patient = patient.groups.filter(name="Patient").exists()
            if not is_patient:
                return Response("Did not specify a Patient", status=status.HTTP_400_BAD_REQUEST)
            
            appointments = patient.appointments
            
            is_receptionist = requester.groups.filter(name="Receptionist").exists()
            if not is_receptionist:
                appointments = appointments.filter(is_approved=True)

            serializer = AppointmentSerializers.AppointmentSerializer(appointments, context={"request": request}, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response("Patient does not exist", status=status.HTTP_404_NOT_FOUND)
        
    @action(detail=True, methods=["get"], url_path="records/last")
    def get_patients_last_record(self, request, pk=None):
        requester = request.user

        is_clinician = requester.groups.filter(name="Clinician").exists()
        if not is_clinician:
            return Response("You are not a Clinician", status=status.HTTP_403_FORBIDDEN)
        
        try:
            patient = User.objects.get(pk=pk)
            is_patient = patient.groups.filter(name="Patient").exists()
            if not is_patient:
                return Response("Did not specify a Patient", status=status.HTTP_400_BAD_REQUEST)
            
            is_provider = PatientClinician.objects.filter(patient=patient, clinician=requester).exists()
            if not is_provider:
                return Response("You are not a provider for this Patient", status=status.HTTP_403_FORBIDDEN)
            
            last_record = PatientData.objects.filter(patient=patient).order_by("created_timestamp").last()
            if not last_record:
                return Response("No records exist", status=status.HTTP_404_NOT_FOUND)
            
            try:
                Log.objects.create(viewed_by=requester, patient_data=last_record)
            except Exception as e :
                return Response({"error": f"Log creation failed: {str(e)}"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
            serializer = PatientDataSerializers.PatientDataVitalsSerializer(last_record)
            return Response(serializer.data)

        except User.DoesNotExist:
            return Response("Patient does not exist", status=status.HTTP_404_NOT_FOUND)
        
    
    @action(detail=True, methods=["get"], url_path="patient/primary-address")
    def get_patient_primary_address(self, request, pk=None):
        requester = request.user
        is_receptionist = requester.groups.filter(name="Receptionist").exists()
        if not is_receptionist:
            return Response({"You are not allowed to view this data"}, status=status.HTTP_403_FORBIDDEN)
        
        patient = User.objects.get(pk=pk)
        primary_address = patient.primary_address
        if not primary_address:
            return Response({"There are no primary addresses for this user"}, status=status.HTTP_403_FORBIDDEN)

        serializer = AddressSerializers.AddressSerializer(primary_address)
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)