import logging
from celery import shared_task
from django.utils import timezone
from django.core.mail import send_mail
from .models import Record, Notification

logger = logging.getLogger(__name__)


@shared_task
def send_follow_up_alerts():
    logger.info("Starting send_follow_up_alerts task")

    now = timezone.now()
    upcoming_followups = Record.objects.filter(
        follow_up_date__gte=now,
        follow_up_date__lte=now + timezone.timedelta(days=1),  # Adjust the timedelta as needed
        notification_sent=False
    )

    for record in upcoming_followups:
        if record.assigned_to:
            message = f"Reminder: You have a follow-up scheduled on {record.follow_up_date.strftime('%Y-%m-%d %H:%M:%S')} for lead: {record.company}"

            # Send an in-app notification
            Notification.objects.create(user=record.assigned_to, message=message)


            # Send an email notification (optional)
            send_mail(
                'Upcoming Follow-Up Reminder',
                message,
                'amey.tecstaq@gmail.com',
                [record.assigned_to.email],
                fail_silently=False,
            )

        # Mark the notification as sent to avoid duplicate notifications
        record.notification_sent = True
        record.save()

    logger.info("Finished send_follow_up_alerts task")
