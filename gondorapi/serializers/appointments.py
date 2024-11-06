from gondorapi.models import Appointment
from gondorapi.serializers import EmbeddedSerializers
from rest_framework import serializers
import datetime


class AppointmentSerializers:
    class AppointmentSerializer(serializers.ModelSerializer):
        clinician = EmbeddedSerializers.EmbeddedUserSimpleSerializer(read_only = True)
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
        

    class AppointmentSimpleSerializer(serializers.ModelSerializer):
        class Meta:
            model = Appointment
            fields = ["id", "scheduled_timestamp"]
        
        def to_representation(self, instance):
            rep = super().to_representation(instance)
            rep["scheduledTimestamp"] = rep.pop("scheduled_timestamp")
            return rep