from django.core.management.base import BaseCommand
from gondorapi.models import User, Appointment, RescheduleRequest
from django.contrib.auth.models import Group
from django.utils.timezone import make_aware
import datetime
import random

class Command(BaseCommand):
    help = "Seed Logs for Patient Data"

    def handle(self, *args, **kwargs):
        reception_group = Group.objects.get(name="Receptionist")
        receptionists = User.objects.filter(groups=reception_group)

        appointments = Appointment.objects.filter(
            is_checked_in=False, 
            scheduled_timestamp__lt=make_aware(datetime.datetime.now())
        )

        requests = []

        for app in appointments:
            is_requested = random.choice([True, False])
            if is_requested:
                approver = None
                is_approved = random.choice([True, False])
                approved_timestamp = None
                requester = app.patient

                now = make_aware(datetime.datetime.now())
                max_seconds = int((now - app.created_timestamp).total_seconds())
                if max_seconds > 0:
                    created_timestamp = app.created_timestamp + datetime.timedelta(
                        seconds=random.randint(1, max_seconds)
                    )
                else:
                    created_timestamp = now
                
                new_timestamp = created_timestamp + datetime.timedelta(
                    minutes=random.randint(1440, 20160)
                )
                
                if is_approved:
                    approver = random.choice(receptionists)
                    max_seconds = max_seconds = int((now - created_timestamp).total_seconds())
                    if max_seconds > 0:
                        approved_timestamp = created_timestamp + datetime.timedelta(
                            seconds=random.randint(1, max_seconds)
                        )
                    else:
                        approved_timestamp = now
                    
                    app.scheduled_timestamp = new_timestamp
                    app.save()
                
                request = RescheduleRequest(
                    appointment = app,
                    requester = requester,
                    approver = approver,
                    is_approved = is_approved,
                    new_timestamp = new_timestamp,
                    created_timestamp = created_timestamp,
                    approved_timestamp = approved_timestamp
                )
                requests.append(request)
        
        RescheduleRequest.objects.bulk_create(requests)
        self.stdout.write(self.style.SUCCESS("Successfully seeded Reschedule Requests"))