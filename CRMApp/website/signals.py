import json

from django.db.models.signals import pre_save, post_save
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_delete
from django.dispatch import receiver
from .models import Record, MeetingRecord, Profile, Notification, DeletedRecord, DeletionHistory
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
                    message = f"Meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %I:%M %p')} for lead:{instance.client_name} from {instance.company} by {instance.last_modified_by.username} from {department} department"
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


@receiver(post_delete, sender=Record)
def handle_record_deletion(sender, instance, **kwargs):
    # Convert datetime objects to strings for serialization
    follow_up_date = instance.follow_up_date.strftime('%Y-%m-%d %H:%M:%S') if instance.follow_up_date else None
    created_at = instance.created_at.strftime('%Y-%m-%d %H:%M:%S') if instance.created_at else None

    # Log detailed deletion history
    DeletionHistory.objects.create(
        record_id=instance.pk,
        record_data=json.dumps({
            'client_name': instance.client_name,
            'company': instance.company,
            'email': instance.email,
            'phone': instance.phone,
            'assigned_to': instance.assigned_to.username if instance.assigned_to else None,
            'department': instance.dept_name,
            'follow_up_date': follow_up_date,
            'remarks': instance.remarks,
            'comments': instance.comments,
            'lead_source': instance.lead_source,
            'created_at': created_at,
        }),
        deleted_by=instance.last_modified_by,  # Assuming you track who deleted it
        deleted_at=timezone.now(),
    )

    # Store basic deleted record info for easy reference
    DeletedRecord.objects.create(
        record_id=instance.pk,
        client_name=instance.client_name,
        company=instance.company,
        email=instance.email,
        phone=instance.phone,
        assigned_to=instance.assigned_to,
        deleted_by=instance.last_modified_by,
        deleted_at=timezone.now(),
        details=json.dumps({
            'department': instance.dept_name,
            'address': instance.address,
            'follow_up_date': follow_up_date,
            'remarks': instance.remarks,
            'comments': instance.comments,
            'lead_source': instance.lead_source,
            'created_at': created_at,
        })
    )