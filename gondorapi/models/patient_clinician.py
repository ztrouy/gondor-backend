from django.db import models
from .user import User
import uuid

class PatientClinician(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clinicians")

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["patient", "clinician"], name="unique_patient_clinician")
        ]
