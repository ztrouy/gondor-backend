from django.db import models
from django.core.validators import MinValueValidator
from .appointment import Appointment
from .user import User
import uuid

class PatientData(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="personal_patient_data")
    appointment = models.ForeignKey(Appointment, on_delete=models.CASCADE, related_name="attached_patient_data")
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="created_patient_data")
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="updated_patient_data")
    created_timestamp = models.DateTimeField(auto_now_add=True)
    updated_timestamp = models.DateTimeField(auto_now=True)
    patient_systolic = models.IntegerField(validators=[MinValueValidator(0)])
    patient_diastolic = models.IntegerField(validators=[MinValueValidator(0)])
    patient_weight_kg = models.DecimalField(max_digits=5, decimal_places=2, validators=[MinValueValidator(0)])
    clinician_notes = models.TextField(blank=True, null=True)
    is_notes_shared = models.BooleanField(default=False)
