from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.response import Response
from gondorapi.models import User, PatientClinician, Address, Appointment
from django.contrib.auth.hashers import check_password
from django.contrib.auth.models import Group
from django.db.models import Q, Value, CharField, Min
from django.db.models.functions import Concat

class ChangePasswordSerializer(serializers.ModelSerializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField()

    class Meta:
        model = User
        fields = ["old_password", "new_password"]
    
    def to_internal_value(self, data):
        data = data.copy()
        data["old_password"] = data.pop("oldPassword")
        data["new_password"] = data.pop("newPassword")
        return super().to_internal_value(data)
    
    def validate(self, attrs):
        validation_errors = check_password(self.validated_data["old_password"], self.instance.password)
        if not validation_errors:
            raise serializers.ValidationError("Old password does not match current password.")
        return super().validate(attrs)

    def update(self, instance, validated_data):
        instance.set_password(validated_data["new_password"])
        instance.save()
        return instance

class UserEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "first_name", "last_name", "date_of_birth"]
    
    def to_internal_value(self, data):
        data = data.copy()
        data["first_name"] = data.pop("firstName")
        data["last_name"] = data.pop("lastName")
        data["date_of_birth"] = data.pop("dateOfBirth")
        return super().to_internal_value(data)

    def update(self, instance, validated_data):
        instance.email = validated_data["email"]
        instance.first_name = validated_data["first_name"]
        instance.last_name = validated_data["last_name"]
        instance.date_of_birth = validated_data["date_of_birth"]
        instance.save()
        return instance

class UserSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "fullName", "date_of_birth", "email"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        rep["dateOfBirth"] = rep.pop("date_of_birth")
        return rep

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
class UserAddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ["line1", "line2", "city", "state_code", "postal_code"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["stateCode"] = rep.pop("state_code")
        rep["postalCode"] = rep.pop("postal_code")
        return rep

class UserWithAddressSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()
    primaryAddress = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "fullName", "date_of_birth", "email", "primaryAddress"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        rep["dateOfBirth"] = rep.pop("date_of_birth")
        return rep

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    
    def get_primaryAddress(self, obj):
        address = obj.primary_address
        if address:
            serialized_address = UserAddressSerializer(address).data
            return serialized_address
        
        return None

class ClinicianSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()

    class Meta:
        model= User
        fields = ["first_name", "last_name", "fullName", "id"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        return rep

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class ClinicianWithIsProviderSerializer(serializers.ModelSerializer):
    isProvider = serializers.SerializerMethodField()
    fullName = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["first_name", "last_name", "fullName", "id", "isProvider"]

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    def get_isProvider(self,obj):
        patient = self.context.get('patient')

        return PatientClinician.objects.filter(patient=patient, clinician=obj).exists()
    
class PatientSerializer(serializers.ModelSerializer):
    fullName = serializers.SerializerMethodField()

    class Meta:
        model= User
        fields = ["first_name", "last_name", "fullName", "date_of_birth", "id"]
    
    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        rep["dateOfBirth"] = rep.pop("date_of_birth")
        return rep

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"
    

class PatientLatestAppointmentSerializer(serializers.ModelSerializer):
    next_approved_appointment = serializers.DateTimeField()
    fullName = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ["first_name", "last_name", "fullName", "date_of_birth", "id", "next_approved_appointment"]

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep["firstName"] = rep.pop("first_name")
        rep["lastName"] = rep.pop("last_name")
        rep["dateOfBirth"] = rep.pop("date_of_birth")
        rep["nextApprovedAppointment"] = rep.pop("next_approved_appointment")
        return rep

    def get_fullName(self, obj):
        return f"{obj.first_name} {obj.last_name}"

class UserViewSet(viewsets.ViewSet):
    @action(detail=False, methods=["get"], url_path="me")
    def get_my_details(self, request):
        serializer = UserWithAddressSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=["put"], url_path="edit-account")
    def edit_account(self, request):
        serializer = UserEditSerializer(request.user, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=["put"], url_path="change-password")
    def change_password(self, request):
        serializer = ChangePasswordSerializer(request.user, request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=["get"], url_path="clinicians")
    def get_all_clinicians(self,request):
        user = request.user

        clinician_group = Group.objects.get(name="Clinician")
        clinicians = User.objects.filter(groups=clinician_group)
         
        is_active_search = self.request.query_params.get('active', None)
        if is_active_search != None:
           clinicians =  clinicians.filter(
                Q(is_active=is_active_search)
            )

        if user.groups.filter(name__in=["Clinician", "Receptionist"]).exists():
            serializer = ClinicianSerializer(clinicians, many=True)
            return Response(serializer.data)
        
        elif user.groups.filter(name="Patient").exists():
            assigned_clinicians = PatientClinician.objects.filter(patient=user).values_list('clinician_id', flat= True)
            serializer = ClinicianWithIsProviderSerializer(clinicians, many= True, context={'patient': user, 'assigned_clinicians':assigned_clinicians})
            return Response(serializer.data)
        
        return Response(status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=["get"], url_path="patients")
    def get_all_active_patients(self,request):
        search_name_text = self.request.query_params.get("name", None)
        is_finding_appointment = self.request.query_params.get("appointment", None)
        
        user = request.user
        patient_group = Group.objects.get(name="Patient")
        patients = User.objects.filter(groups=patient_group)

        if search_name_text:
            patients = patients.annotate(
                full_name=Concat('first_name', Value(' '), 'last_name', output_field=CharField())
            ).filter(
                Q(first_name__icontains=search_name_text) |
                Q(last_name__icontains=search_name_text) |
                Q(full_name__icontains=search_name_text)
            )

        if user.groups.filter(name__in=["Clinician", "Receptionist"]).exists():
            if is_finding_appointment:
                patients = patients.annotate(
                    next_approved_appointment=Min(
                        'appointments__scheduled_timestamp',
                        filter=Q(appointments__approved_timestamp__isnull=False)
                    )
                )

                serializer = PatientLatestAppointmentSerializer(patients, many=True)
                return Response(serializer.data)
            
            else:
                serializer = PatientSerializer(patients, many=True)
                return Response(serializer.data)

        return Response(status=status.HTTP_403_FORBIDDEN)

          

