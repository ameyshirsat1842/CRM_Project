from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from .models import Notification, Record, MeetingRecord


@receiver(post_save, sender=Record)
def create_lead_notification(sender, instance, created, **kwargs):
    if created:
        if instance.assigned_to:
            message = f"Lead '{instance.client_name}' has been assigned to {instance.assigned_to.username} by {instance.created_by.username}."
            Notification.objects.create(user=instance.assigned_to, message=message)
    else:
        if instance.assigned_to:
            message = f"Lead '{instance.client_name}' has been updated and is assigned to {instance.assigned_to.username} by {instance.created_by.username}."
            Notification.objects.create(user=instance.assigned_to, message=message)


@receiver(post_save, sender=MeetingRecord)
def create_meeting_notification(sender, instance, **kwargs):
    if instance.follow_up_date and instance.follow_up_date == timezone.now().date():
        message = f"Follow up for meeting with {instance.meeting_partner} is due today."
        Notification.objects.create(user=instance.created_by, message=message)
