from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import Record


@shared_task
def notify_new_lead(record_id):
    try:
        record = Record.objects.get(id=record_id)
        if record.assigned_to:
            send_mail(
                'New Lead Assigned to You',
                f'A new lead "{record.company}" has been assigned to you.',
                'from@example.com',
                [record.assigned_to.email],
                fail_silently=False,
            )
    except Record.DoesNotExist:
        pass


@shared_task
def notify_lead_assignment(record_id):
    try:
        record = Record.objects.get(id=record_id)
        if record.assigned_to:
            send_mail(
                'Lead Reassigned to You',
                f'The lead "{record.company}" has been reassigned to you.',
                'from@example.com',
                [record.assigned_to.email],
                fail_silently=False,
            )
    except Record.DoesNotExist:
        pass


@shared_task
def send_notifications():
    now = timezone.now()
    records = Record.objects.filter(
        follow_up_date__lte=now,
        notification_sent=False
    )
    for record in records:
        if record.created_by:
            send_mail(
                'Upcoming Follow-Up for Your Lead',
                f'Reminder: The lead "{record.company}" you created has a follow-up scheduled for {record.follow_up_date}.',
                'from@example.com',
                [record.created_by.email],  # Send email to the user who created the lead
                fail_silently=False,
            )
        record.notification_sent = True
        record.save()
