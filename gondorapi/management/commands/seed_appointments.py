from django.core.management.base import BaseCommand
from gondorapi.models import User, Appointment
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
import datetime
import random

class Command(BaseCommand):
    help = "Seed Appointments for Users with the Group 'Patient'"

    def handle(self, *args, **kwargs):
        clinician_group = Group.objects.get(name="Clinician")
        reception_group = Group.objects.get(name="Receptionist")
        patient_group = Group.objects.get(name="Patient")

        clinicians = User.objects.filter(groups=clinician_group)
        receptionists = User.objects.filter(groups=reception_group)
        patients = User.objects.filter(groups=patient_group)

        appointments = []

        for patient in patients:
            num_appointments = random.randint(2, 6)
            for _ in range(num_appointments):
                days_ago = random.randint(1, 7)
                created_timestamp = make_aware(datetime.datetime.now() - datetime.timedelta(days=days_ago))
                clinician = random.choice(clinicians)
                is_approved = random.choice([True, False])
                approver = None
                approved_timestamp = None
                scheduled_timestamp = None

                now = make_aware(datetime.datetime.now())

                if is_approved:
                    approver = random.choice(receptionists)
                    approved_timestamp = created_timestamp + datetime.timedelta(
                        seconds=random.randint(1, int((now - created_timestamp).total_seconds()))
                    )

                is_checked_in = random.choice([True, False])
                if not is_approved:
                    is_checked_in = False
                    scheduled_timestamp = now + datetime.timedelta(
                        minutes=random.randint(-10080, -1440)
                    )

                if is_checked_in:
                    scheduled_timestamp = now + datetime.timedelta(
                        minutes=random.randint(-1440, 30)
                    )
                elif is_approved:
                    scheduled_timestamp = now + datetime.timedelta(
                        minutes=random.randint(-30, 4320)
                    )

                appointment = Appointment(
                    patient=patient,
                    clinician=clinician,
                    is_approved=is_approved,
                    approver=approver,
                    created_timestamp=created_timestamp,
                    approved_timestamp=approved_timestamp,
                    is_checked_in=is_checked_in,
                    scheduled_timestamp=scheduled_timestamp
                )
                appointments.append(appointment)

        Appointment.objects.bulk_create(appointments)
        self.stdout.write(self.style.SUCCESS(f"Successfully seeded {len(appointments)} Appointment(s)"))
