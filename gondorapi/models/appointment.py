from django.db import models
from .user import User
import uuid

class Appointment(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="appointments")
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clinician_appointments")
    approver = models.ForeignKey(User, on_delete=models.CASCADE, related_name="approved_appointments")
    is_approved = models.BooleanField(default=False)
    is_checked_in = models.BooleanField(default=False)
    created_timestamp = models.DateTimeField(auto_now_add=True)
    scheduled_timestamp = models.DateTimeField()
