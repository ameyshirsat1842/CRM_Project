# CRMApp/tasks.py

from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from website.models import Record, Notification


@shared_task
def check_reminders():
    today = timezone.now().date()
    tomorrow = today + timedelta(days=1)

    records_to_remind = Record.objects.filter(follow_up_date=tomorrow)

    for record in records_to_remind:
        user = record.assigned_person  # Assuming assigned_person is a User instance
        message = "Reminder: Follow-up for {record.company} is tomorrow."
        Notification.objects.create(user=user, message=message)
