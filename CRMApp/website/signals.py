from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Record, MeetingRecord, Profile, Notification
from .notifications import send_notification_to_user
from .utils import send_otp_to_email


@receiver(pre_save, sender=Record)
def notify_user_assignment(sender, instance, **kwargs):
    try:
        if instance.pk:  # Existing Record
            old_record = Record.objects.get(pk=instance.pk)

            # Handle reassignment notifications
            if old_record.assigned_to != instance.assigned_to:
                new_assignee = instance.assigned_to
                if new_assignee:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by, 'profile') else 'Unknown'
                    message = f"You have been assigned a new lead: {instance.client_name} from {instance.company} by {instance.last_modified_by.username} from {department} department"
                    send_notification_to_user(new_assignee, message)
                    Notification.objects.create(user=new_assignee, message=message)

            # Handle follow-up date update notifications
            if old_record.follow_up_date != instance.follow_up_date and instance.follow_up_date:
                assignee = instance.assigned_to
                if assignee:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by, 'profile') else 'Unknown'
                    message = f"Meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %I:%M %p')} for lead: {instance.company} by {instance.last_modified_by.username} from {department} department"
                    send_notification_to_user(assignee, message)
                    Notification.objects.create(user=assignee, message=message)
        else:
            # New Record creation and assignment
            if instance.assigned_to:
                new_assignee = instance.assigned_to
                department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by, 'profile') else 'Unknown'
                message = f"You have been assigned a new lead: {instance.client_name} from {instance.company} by {instance.last_modified_by.username} from {department} department"
                send_notification_to_user(new_assignee, message)
                Notification.objects.create(user=new_assignee, message=message)
    except Record.DoesNotExist:
        pass  # Handle case where old_record does not exist


@receiver(pre_save, sender=MeetingRecord)
def notify_meeting_follow_up(sender, instance, **kwargs):
    try:
        if instance.pk:  # Existing MeetingRecord
            old_meeting = MeetingRecord.objects.get(pk=instance.pk)
            if old_meeting.follow_up_date != instance.follow_up_date and instance.follow_up_date:
                speaker = instance.speaker
                if speaker:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by, 'profile') else 'Unknown'
                    message = f"You have a follow-up meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %I:%M %p')} with {instance.meeting_partner} by {instance.last_modified_by.username} from {department} department"
                    send_notification_to_user(speaker, message)
                    Notification.objects.create(user=speaker, message=message)
    except MeetingRecord.DoesNotExist:
        pass  # Handle case where old_meeting does not exist


@receiver(post_save, sender=User)
def manage_user_creation(sender, instance, created, **kwargs):
    if created:
        # Create profile and send OTP when a new user is created
        Profile.objects.create(user=instance)
        send_otp_to_email(instance)  # Send OTP when a new user is created
    else:
        # Update the user's profile on save
        instance.profile.save()

