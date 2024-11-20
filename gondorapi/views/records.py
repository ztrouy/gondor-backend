from gondorapi.models import PatientData, Log, PatientClinician, Appointment
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from gondorapi.serializers import PatientDataSerializers
from django.db.models import Q
from django.shortcuts import get_object_or_404


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
            serializer = PatientDataSerializers.PatientDataSimpleSerializer(records, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response({"error": "Unauthorized access. Only patients can access their records"}, status=status.HTTP_400_BAD_REQUEST)
    
    def retrieve(self,request, pk=None):
        user = request.user
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

        serializer = PatientDataSerializers.PatientDataSerializer(found_record)
        return Response(serializer.data)
    
    def update(self, request, pk=None):
        requester = request.user
        is_clinician = requester.groups.filter(name="Clinician").exists()
        if not is_clinician:
            return Response("You are not a Clinician", status=status.HTTP_403_FORBIDDEN)
        
        try:
            record = PatientData.objects.get(pk=pk)
            patient = record.patient

            is_provider = PatientClinician.objects.filter(patient=patient, clinician=requester).exists()
            is_creator = requester == record.created_by
            if not is_provider and not is_creator:
                return Response("You are not allowed to edit this Medical Record", status=status.HTTP_403_FORBIDDEN)
            
            serializer = PatientDataSerializers.PatientDataEditSerializer(record, request.data, context={"request": request})
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_204_NO_CONTENT)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except PatientData.DoesNotExist:
            return Response("Medical Record does not exist", status=status.HTTP_404_NOT_FOUND)  
          
    def create(self,request):
        user = request.user

        authorized_user = user.groups.filter(name="Clinician").exists()
        if not authorized_user:
            return Response({"You are not authorized"}, status=status.HTTP_403_FORBIDDEN)
        
        appointment_id = request.data["appointment"]
        try:
            appointment = Appointment.objects.get(pk = appointment_id)

            existing_record = PatientData.objects.filter(appointment = appointment)
            if existing_record:
                return Response({"Message": "Record already exists for this appointment"}, status=status.HTTP_409_CONFLICT)

            serializer = PatientDataSerializers.PatientDataCreateSerializer(data=request.data, context={"request": request})
            if serializer.is_valid():
                patient_data = serializer.save()

                return Response(patient_data.id, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        except Appointment.DoesNotExist:
            return Response({"Appointment does not exist"}, status=status.HTTP_400_BAD_REQUEST)
        
    
    @action(detail=True, methods=["put"], url_path="unshare")
    def unshare_notes(self,request,pk=None):
        requester = request.user
        is_clinician = requester.groups.filter(name="Clinician").exists()
        if not is_clinician:
            return Response("You are not a Clinician", status=status.HTTP_403_FORBIDDEN)
        
        try:
            record = PatientData.objects.get(pk=pk)
            patient = record.patient

            is_provider = PatientClinician.objects.filter(patient=patient, clinician=requester).exists()
            is_creator = requester == record.created_by
            if not is_provider and not is_creator:
                return Response("You are not allowed to edit this Medical Record", status=status.HTTP_403_FORBIDDEN)
            
            if record.is_notes_shared == False:
                return Response({"Notes already not shared."}, status=status.HTTP_400_BAD_REQUEST)
            
            record.is_notes_shared = False
            record.save()
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        except Appointment.DoesNotExist:
            return Response({"Appointment does not exist"}, status=status.HTTP_404_NOT_FOUND)
        
       


    

