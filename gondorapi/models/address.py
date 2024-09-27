from django.db import models
import uuid

class Address(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    line1 = models.CharField(max_length=50)
    line2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50)
    state_code = models.CharField(max_length=2)
    postal_code = models.CharField(max_length=10)