from django.db import models
from .appointment import Appointment
from .user import User
import uuid

class RescheduleRequest(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE)
    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name="reschedule_requests")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, null=True, related_name="approved_reschedules")
    is_approved = models.BooleanField(default=False)
    new_timestamp = models.DateTimeField()
    created_timestamp = models.DateTimeField(auto_now_add=True)
    approved_timestamp = models.DateTimeField(auto_now=True, null=True)
