from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from .models import Record, Notification


class Command(BaseCommand):
    help = 'Check and send reminders for upcoming follow-up dates'

    def handle(self, *args, **options):
        today = timezone.now().date()
        tomorrow = today + timedelta(days=1)

        records_to_remind = Record.objects.filter(follow_up_date=tomorrow)

        for record in records_to_remind:
            user = record.assigned_person  # Assuming assigned_person is a User instance
            message = "Reminder: Follow-up for {record.company} is tomorrow."
            Notification.objects.create(user=user, message=message)

        self.stdout.write(self.style.SUCCESS('Reminders checked successfully.'))
