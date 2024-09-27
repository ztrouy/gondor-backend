from django.db import models

class State(models.Model):
    state_code = models.CharField(max_length=2, primary_key=True)
    name = models.CharField(max_length=50)
