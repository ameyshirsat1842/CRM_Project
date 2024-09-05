from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from .models import Record, MeetingRecord, Profile, Notification
from .notifications import send_notification_to_user
from django.contrib.auth.models import User
from .utils import send_otp_to_email


@receiver(pre_save, sender=Record)
def notify_user_assignment(sender, instance, **kwargs):
    if instance.pk:  # Check if the record already exists (not a new creation)
        old_record = Record.objects.get(pk=instance.pk)

        # Check for reassignment
        if old_record.assigned_to != instance.assigned_to:
            new_assignee = instance.assigned_to
            if new_assignee:
                department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by,
                                                                                     'profile') else 'Unknown'
                message = f"You have been assigned a new lead: {instance.client_name} from {instance.company} by {instance.last_modified_by.username} from the {department} department"
                send_notification_to_user(new_assignee, message)
                Notification.objects.create(user=new_assignee, message=message)

        # Check for follow-up date update
        if old_record.follow_up_date != instance.follow_up_date:
            if instance.follow_up_date:
                assignee = instance.assigned_to
                if assignee:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by,
                                                                                         'profile') else 'Unknown'
                    message = f"Meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d')} for lead: {instance.company} by {instance.last_modified_by.username} from the {department} department"
                    send_notification_to_user(assignee, message)
                    Notification.objects.create(user=assignee, message=message)
    else:
        # Handle new lead creation and assignment
        if instance.assigned_to:
            new_assignee = instance.assigned_to
            department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by,
                                                                                 'profile') else 'Unknown'
            message = f"You have been assigned a new lead: {instance.client_name} from {instance.company} by {instance.last_modified_by.username} from the {department} department"
            send_notification_to_user(new_assignee, message)
            Notification.objects.create(user=new_assignee, message=message)


@receiver(pre_save, sender=MeetingRecord)
def notify_meeting_follow_up(sender, instance, **kwargs):
    if instance.pk:  # Check if the meeting record already exists
        old_meeting = MeetingRecord.objects.get(pk=instance.pk)
        if old_meeting.follow_up_date != instance.follow_up_date:
            if instance.follow_up_date:
                speaker = instance.speaker
                if speaker:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by,
                                                                                         'profile') else 'Unknown'
                    message = f"You have a follow-up meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d')} with {instance.meeting_partner} by {instance.last_modified_by.username} from the {department} department"
                    send_notification_to_user(speaker, message)
                    Notification.objects.create(user=speaker, message=message)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()


@receiver(post_save, sender=User)
def send_otp_on_user_creation(sender, instance, created, **kwargs):
    if created:
        send_otp_to_email(instance)  # Send OTP when a new user is created
