from django.core.management.base import BaseCommand
from gondorapi.models import User, Appointment, PatientData, PatientClinician
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
import datetime
import random

class Command(BaseCommand):
    help = "Seed Patient Data for Appointments that are completed"

    def handle(self, *args, **kwargs):
        clinician_group = Group.objects.get(name="Clinician")
        clinicians = User.objects.filter(groups=clinician_group)
        appointments = Appointment.objects.filter(is_checked_in=True)

        patient_datas = []

        for appointment in appointments:
            patient = appointment.patient
            appointment = appointment
            appointment_clinician = appointment.clinician
            created_timestamp = appointment.scheduled_timestamp + datetime.timedelta(minutes=25)
            patient_systolic = random.randint(105, 185)
            patient_diastolic = random.randint(70, 125)
            patient_weight_kg = random.randint(40, 130)
            updated_by = None
            updated_timestamp = None
            is_notes_shared = random.choice([True, False])

            is_updated = random.choice([True, False])

            if is_updated:
                patient_clinicians = PatientClinician.objects.filter(patient=patient).values_list("clinician", flat=True)
                elibile_clinicians = clinicians.filter(id__in=list([appointment_clinician.id] + list(patient_clinicians)))
                updated_by = random.choice(elibile_clinicians)
                
                now = make_aware(datetime.datetime.now())
                max_seconds = int((now - created_timestamp).total_seconds())
                if max_seconds > 0:
                    updated_timestamp = created_timestamp + datetime.timedelta(
                        seconds=random.randint(1, max_seconds)
                    )
                else:
                    updated_timestamp = created_timestamp
            
            weight_notes = "Patient is a healthy weight."
            if patient_weight_kg < 58:
                weight_notes = "Patient is underweight."
            elif patient_weight_kg > 85:
                weight_notes = "Patient is overweight."

            bp_notes = "Patient has healthy blood pressure."
            if patient_systolic >= 180 or patient_diastolic >= 120:
                bp_notes = "Patient is having a hypertensive crisis, and was recommended to go to the ER."
            elif patient_systolic >= 140 or patient_diastolic >= 90:
                bp_notes = "Patient has Stage 2 high blood pressure."
            elif patient_systolic >= 130 or patient_diastolic >= 80:
                bp_notes = "Patient has Stage 1 high blood pressure."
            elif patient_systolic >= 120 and patient_diastolic < 80:
                bp_notes = "Patient has elevated blood pressure."
            
            secret_notes = "This note was shared with the patient."
            if not is_notes_shared:
                secret_notes = "This note was not shared with the patient by default."
            
            patient_data = PatientData(
                patient = patient,
                appointment = appointment,
                created_by = appointment_clinician,
                updated_by = updated_by,
                created_timestamp = created_timestamp,
                updated_timestamp = updated_timestamp,
                patient_systolic = patient_systolic,
                patient_diastolic = patient_diastolic,
                patient_weight_kg = patient_weight_kg,
                clinician_notes = f"{weight_notes} {bp_notes} {secret_notes}",
                is_notes_shared = is_notes_shared
            )
            patient_datas.append(patient_data)
        
        PatientData.objects.bulk_create(patient_datas)
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(patient_datas)} Patient Data"))
            