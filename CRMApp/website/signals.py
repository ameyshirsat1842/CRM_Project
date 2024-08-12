from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Record, MeetingRecord
from .notifications import send_notification_to_user
from datetime import datetime


@receiver(pre_save, sender=Record)
def notify_user_assignment(sender, instance, **kwargs):
    if instance.pk:  # Check if the record already exists (not a new creation)
        old_record = Record.objects.get(pk=instance.pk)

        # Check for reassignment
        if old_record.assigned_to != instance.assigned_to:
            new_assignee = instance.assigned_to
            if new_assignee:
                message = f"You have been assigned a new lead: {instance.client_name} from {instance.company}"
                send_notification_to_user(new_assignee, message)

        # Check for follow-up date update
        if old_record.follow_up_date != instance.follow_up_date:
            if instance.follow_up_date:
                assignee = instance.assigned_to
                if assignee:
                    message = f"Follow-up scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %H:%M:%S')} for lead: {instance.company}"
                    send_notification_to_user(assignee, message)


@receiver(pre_save, sender=MeetingRecord)
def notify_meeting_follow_up(sender, instance, **kwargs):
    if instance.pk:  # Check if the meeting record already exists
        old_meeting = MeetingRecord.objects.get(pk=instance.pk)
        if old_meeting.follow_up_date != instance.follow_up_date:
            if instance.follow_up_date:
                speaker = instance.speaker
                if speaker:
                    message = f"You have a follow-up meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %H:%M:%S')} regarding your meeting with {instance.meeting_partner}"
                    send_notification_to_user(speaker, message)
