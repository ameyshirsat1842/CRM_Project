from django.contrib.auth.models import User
from django.db.models.signals import post_delete
from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.urls import reverse
from django.utils import timezone
from .models import Record, MeetingRecord, Profile, Notification, DeletedRecord, Ticket, Customer
from .notifications import send_notification_to_user
from .utils import send_otp_to_email


@receiver(pre_save, sender=Record)
def notify_user_assignment_pre_save(sender, instance, **kwargs):
    # Only handle updates to existing records in pre_save
    try:
        if instance.pk:  # Existing Record
            old_record = Record.objects.get(pk=instance.pk)

            # Handle reassignment notifications
            if old_record.assigned_to != instance.assigned_to:
                new_assignee = instance.assigned_to
                if new_assignee:
                    last_modified_by = instance.last_modified_by or instance.created_by
                    department = (
                        last_modified_by.profile.department if last_modified_by and hasattr(last_modified_by, 'profile')
                        else 'Unknown'
                    )
                    message = (
                        f"You have been re-assigned a lead: {instance.client_name} from {instance.company} "
                        f"by {last_modified_by.username if last_modified_by else 'an admin'} from {department} department"
                    )
                    send_notification_to_user(new_assignee, message)
                    Notification.objects.create(
                        user=new_assignee,
                        message=message,
                        link_url=reverse('record', kwargs={'pk': instance.pk})
                    )

            # Handle follow-up date update notifications
            if old_record.follow_up_date != instance.follow_up_date and instance.follow_up_date:
                assignee = instance.assigned_to
                if assignee:
                    last_modified_by = instance.last_modified_by or instance.created_by
                    department = (
                        last_modified_by.profile.department if last_modified_by and hasattr(last_modified_by, 'profile')
                        else 'Unknown'
                    )
                    message = (
                        f"Meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %I:%M %p')} for lead: "
                        f"{instance.client_name} from {instance.company} by {last_modified_by.username if last_modified_by else 'an admin'} from {department} department"
                    )
                    send_notification_to_user(assignee, message)
                    Notification.objects.create(
                        user=assignee,
                        message=message,
                        link_url=reverse('record', kwargs={'pk': instance.pk})
                    )
    except Record.DoesNotExist:
        pass


@receiver(post_save, sender=Record)
def notify_user_assignment_post_save(sender, instance, created, **kwargs):
    # Handle notifications for new records in post_save
    if created and instance.assigned_to:
        new_assignee = instance.assigned_to
        created_by = instance.created_by
        department = (
            created_by.profile.department if created_by and hasattr(created_by, 'profile')
            else 'Unknown'
        )
        message = (
            f"You have been assigned a new lead: {instance.client_name} from {instance.company} by "
            f"{created_by.username if created_by else 'an admin'} from {department} department"
        )
        send_notification_to_user(new_assignee, message)
        Notification.objects.create(
            user=new_assignee,
            message=message,
            link_url=reverse('record', kwargs={'pk': instance.pk})
        )


@receiver(pre_save, sender=MeetingRecord)
def notify_meeting_follow_up(sender, instance, **kwargs):
    try:
        if instance.pk:  # Existing MeetingRecord
            old_meeting = MeetingRecord.objects.get(pk=instance.pk)
            if old_meeting.follow_up_date != instance.follow_up_date and instance.follow_up_date:
                speaker = instance.speaker
                if speaker:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by,
                                                                                         'profile') else 'Unknown'
                    message = f"You have a follow-up meeting scheduled on {instance.follow_up_date.strftime('%Y-%m-%d %I:%M %p')} with {instance.meeting_partner} by {instance.last_modified_by.username} from {department} department"
                    send_notification_to_user(speaker, message)
                    Notification.objects.create(user=speaker, message=message, link_url=f'/record/{instance.pk}')
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
    # Convert datetime objects for deletion
    follow_up_date = instance.follow_up_date if instance.follow_up_date else None
    created_at = instance.created_at if instance.created_at else None

    # Ensure deletion_reason is available
    deletion_reason = getattr(instance, 'deletion_reason', 'No reason provided')

    # Log the deleted record's details
    DeletedRecord.objects.create(
        record_id=instance.pk,
        client_name=instance.client_name,
        company=instance.company,
        email=instance.email,
        phone=instance.phone,
        assigned_to=instance.assigned_to,
        deleted_by=instance.last_modified_by,  # Ensure this tracks the deleting user
        deleted_at=timezone.now(),
        department=instance.dept_name,
        address=instance.address,
        follow_up_date=follow_up_date,
        remarks=instance.remarks,
        comments=instance.comments,
        lead_source=instance.lead_source,
        deletion_reason=deletion_reason
    )

    # Notify the assigned user
    if instance.assigned_to:
        notification_message = f"Your lead {instance.client_name} from {instance.company} has been deleted by {instance.last_modified_by.username}."
        send_notification_to_user(instance.assigned_to, notification_message)

        # Optionally save the notification to the database with link to the deleted record
        Notification.objects.create(
            user=instance.assigned_to,
            message=notification_message,
            link_url=f'/deleted-record/{instance.pk}'
        )


# Signal for notifying user when a ticket is assigned or reassigned
@receiver(pre_save, sender=Ticket)
def notify_user_ticket_assignment(sender, instance, **kwargs):
    try:
        if instance.pk:  # Existing Ticket
            old_ticket = Ticket.objects.get(pk=instance.pk)

            # Check if the ticket is reassigned
            if old_ticket.assigned_to != instance.assigned_to:
                new_assignee = instance.assigned_to
                assigner = instance.last_modified_by  # Assumed the last modified user is the assigner

                if new_assignee:
                    # Notify the new assignee
                    due_date_str = instance.due_date.strftime('%b %d, %Y %I:%M %p') if instance.due_date else "No due date"
                    message = f"You have been assigned a new ticket: {instance.title} by {assigner.username}. Due date: {due_date_str}."
                    send_notification_to_user(new_assignee, message)
                    Notification.objects.create(user=new_assignee, message=message, link_url=f'/ticket/{instance.pk}')

                # Optionally notify the old assignee that they are no longer assigned
                if old_ticket.assigned_to:
                    message = f"You have been unassigned from the ticket: {instance.title}."
                    send_notification_to_user(old_ticket.assigned_to, message)
                    Notification.objects.create(user=old_ticket.assigned_to, message=message,
                                                link_url=f'/ticket/{instance.pk}')
        else:
            # New Ticket assignment
            if instance.assigned_to:
                new_assignee = instance.assigned_to
                assigner = instance.created_by  # Assumed the creator is the assigner
                due_date_str = instance.due_date.strftime('%b %d, %Y %I:%M %p') if instance.due_date else "No due date"
                message = f"You have been assigned a new ticket: {instance.title} by {assigner.username}. Due date: {due_date_str}."
                send_notification_to_user(new_assignee, message)
                Notification.objects.create(user=new_assignee, message=message, link_url=f'/ticket/{instance.pk}')

    except Ticket.DoesNotExist:
        pass  # Handle case where old_ticket does not exist


@receiver(pre_save, sender=Customer)
def notify_user_customer_assignment(sender, instance, **kwargs):
    try:
        if instance.pk:  # Existing customer
            old_customer = Customer.objects.get(pk=instance.pk)

            # Check if the customer is being reassigned
            if old_customer.assigned_to != instance.assigned_to:
                new_assignee = instance.assigned_to
                if new_assignee:
                    department = instance.last_modified_by.profile.department if hasattr(instance.last_modified_by, 'profile') else 'Unknown'
                    message = f"You have been re-assigned a customer: {instance.client_name} from {instance.company} by {instance.last_modified_by.username} from {department} department"
                    link_url = reverse('customer_detail', kwargs={'customer_id': instance.pk})  # Correct URL
                    send_notification_to_user(new_assignee, message)
                    Notification.objects.create(user=new_assignee, message=message, link_url=link_url)

        else:  # New customer assignment
            if instance.assigned_to:
                new_assignee = instance.assigned_to
                department = instance.created_by.profile.department if hasattr(instance.created_by, 'profile') else 'Unknown'
                message = f"You have been assigned a new customer: {instance.client_name} from {instance.company} by {instance.created_by.username} from {department} department"
                link_url = reverse('customer_detail', kwargs={'customer_id': instance.pk})  # Correct URL
                send_notification_to_user(new_assignee, message)
                Notification.objects.create(user=new_assignee, message=message, link_url=link_url)

    except Customer.DoesNotExist:
        pass
