from django.db import models
from .user import User

class PatientClinician(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, related_name="patients")
    clinician = models.ForeignKey(User, on_delete=models.CASCADE, related_name="clinicians")
