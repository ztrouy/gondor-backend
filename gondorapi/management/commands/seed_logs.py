from django.core.management.base import BaseCommand
from gondorapi.models import User, PatientData, PatientClinician, Log
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
import datetime
import random

class Command(BaseCommand):
    help = "Seed Logs for Patient Data"

    def handle(self, *args, **kwargs):
        clinician_group = Group.objects.get(name="Clinician")
        clinicians = User.objects.filter(groups=clinician_group)
        patient_datas = PatientData.objects.all()

        logs = []
        
        for patient_data in patient_datas:
            num_logs = random.randint(3, 15)
            for _ in range(num_logs):
                patient_clinicians = PatientClinician.objects.filter(patient=patient_data.patient).values_list("clinician", flat=True)
                appointment_clinician = patient_data.created_by
                eligible_clinicians = clinicians.filter(id__in=list([appointment_clinician.id] + list(patient_clinicians)))
                eligible_viewers = list(eligible_clinicians)
                
                if appointment_clinician not in eligible_viewers:
                    eligible_viewers.append(appointment_clinician)
                
                if patient_data.patient not in eligible_viewers:
                    eligible_viewers.append(patient_data.patient)

                viewed_by = random.choice(eligible_viewers)
                
                now = make_aware(datetime.datetime.now())
                max_seconds = int((now - patient_data.created_timestamp).total_seconds())
                if max_seconds > 0:
                    created_timestamp = patient_data.created_timestamp + datetime.timedelta(
                        seconds=random.randint(1, max_seconds)
                    )
                else:
                    created_timestamp = patient_data.created_timestamp

                log = Log(
                    patient_data = patient_data,
                    viewed_by = viewed_by,
                    created_timestamp = created_timestamp
                )
                logs.append(log)
        
        Log.objects.bulk_create(logs)
        self.stdout.write(self.style.SUCCESS("Successfully seeded Logs"))