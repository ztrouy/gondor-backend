from django.contrib import admin
from django.contrib.auth.models import Group

# Register your models here.
Group.objects.create(name="Patient")
Group.objects.create(name="Clinician")
Group.objects.create(name="Receptionist")
Group.objects.create(name="Administrator")