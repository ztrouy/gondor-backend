from django.db import models
from .patient_data import PatientData
from .user import User
import uuid

class Log(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    viewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="viewed_patient_data")
    patient_data = models.ForeignKey(PatientData, on_delete=models.CASCADE, related_name="view_logs")
    created_timestamp = models.DateTimeField(auto_now_add=True)
