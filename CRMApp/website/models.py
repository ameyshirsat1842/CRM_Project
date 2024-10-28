from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class Record(models.Model):
    # Fields
    DoesNotExist = None
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.CharField(max_length=50, null=True, blank=True)
    client_name = models.CharField(max_length=50, null=True, blank=True)
    dept_name = models.CharField(max_length=50, null=True, blank=True)
    phone = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits.")]
    )
    phone_2 = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits.")],
        null=True,
        blank=True
    )

    email = models.EmailField(max_length=100)
    email_2 = models.EmailField(max_length=100, null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='assigned_leads',
        null=True,
        blank=True
    )
    last_modified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='modified_records',
        null=True,
        blank=True
    )
    follow_up_date = models.DateTimeField(null=True, blank=True)
    follow_up_attended = models.BooleanField(default=False)
    comments = models.CharField(max_length=200, null=True, blank=True)
    remarks = models.CharField(max_length=200, null=True, blank=True)
    visible_to = models.ManyToManyField(User, related_name='visible_records', blank=True)
    is_converted = models.BooleanField(default=False)
    attachments = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True
    )
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        related_name='created_records',
        null=True
    )
    social_media_details = models.TextField(null=True, blank=True)

    # Classification Choices
    CLASSIFICATION_CHOICES = (
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
        ('dead', 'Dead'),
        ('in_progress', 'In Progress'),
    )
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='unassigned')

    # Lead Source Choices
    LEAD_SOURCE_CHOICES = [
        ('BNI Connect', 'BNI Connect'),
        ('LinkedIn', 'LinkedIn'),
        ('Google', 'Google'),
        ('Event', 'Event'),
        ('Reference', 'Reference'),
        ('Walk in', 'Walk in'),
        ('Social Media', 'Social Media'),
        ('Other Source', 'Other Source'),
    ]
    lead_source = models.CharField(
        max_length=50,
        choices=LEAD_SOURCE_CHOICES,
        blank=True,
        null=True,
        default='Other Source'
    )
    # Priority Choices
    PRIORITY_CHOICES = [
        ('high', 'High'),
        ('mid', 'Mid'),
        ('low', 'Low'),
    ]
    priority = models.CharField(
        max_length=10,
        choices=PRIORITY_CHOICES,
        default='mid'
    )
    value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    objects = models.Manager()  # Default manager

    # String representation
    def __str__(self):
        return f"Record({self.company}, {self.client_name}, {self.phone})"

    # Meta options
    class Meta:
        verbose_name = 'Record'
        verbose_name_plural = 'Records'
        indexes = [
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_at']),
        ]

    # Custom methods and properties
    @property
    def full_address(self):
        return f"{self.address}, {self.city}"

    def get_follow_up_status(self):
        if self.follow_up_date:
            if self.follow_up_date < timezone.now().date():
                return "Overdue"
            return "Upcoming"
        return "No follow-up scheduled"


class Customer(models.Model):
    # Basic customer information
    DoesNotExist = None
    company = models.CharField(max_length=255, blank=True, null=True)
    client_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=15, blank=True, null=True)
    email = models.EmailField(unique=True)

    # Address information
    address = models.TextField(blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)

    # Additional customer details
    dept_name = models.CharField(max_length=255, blank=True, null=True)
    lead_source = models.CharField(max_length=255, blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    comments = models.TextField(blank=True, null=True)

    # Tracking the assignment and history of the customer
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                    related_name='assigned_customers')
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                   related_name='created_customers')
    created_at = models.DateTimeField(auto_now_add=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True,
                                         related_name='modified_customers')
    last_modified_at = models.DateTimeField(auto_now=True)

    classification = models.CharField(
        max_length=50,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('converted', 'Converted'),
            ('lead', 'Lead'),
            ('customer', 'Customer'),
        ],
        default='Converted'
    )
    # Financial Information
    bank_details = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True
    )
    gst_number = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True
    )
    msme = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True
    )
    pancard = models.FileField(
        upload_to='attachments/',
        null=True,
        blank=True
    )
    objects = models.Manager()  # Default manager

    def __str__(self):
        return f"{self.client_name} ({self.company})"


class NotificationManager(models.Manager):
    def unread_for_user(self, user):
        return self.filter(user=user, is_read=False)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link_url = models.CharField(max_length=255, blank=True, null=True)  # To store the URL link
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    objects = NotificationManager()

    def __str__(self):
        return 'Notification for {self.user.username}: {self.message}'

    def mark_as_read(self):
        self.is_read = True
        self.save()


class Ticket(models.Model):
    # Define the choices for ticket_type
    DoesNotExist = None
    objects = None
    TICKET_TYPE_CHOICES = [
        ('Acronis Backup Support', 'Acronis Backup Support'),
        ('Cloud Meetings', 'Cloud Meetings'),
        ('Email Support', 'Email Support'),
        ('General Inquiry', 'General Inquiry'),
        ('Marketing Leads', 'Marketing Leads'),
        ('On-Premises Support', 'On-Premises Support'),
        ('Sales', 'Sales'),
        ('Server/Network Support', 'Server/Network Support'),
    ]

    # Define the choices for support_mode
    SUPPORT_MODE_CHOICES = [
        ('On Site', 'On Site'),
        ('Remote', 'Remote'),
    ]
    # Define status choices
    STATUS_CHOICES = [
        ('In Progress', 'In Progress'),
        ('Dead', 'Dead'),
        ('Closed', 'Closed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField()
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, related_name='tickets',null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tickets_created")
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    company_name = models.CharField(max_length=200, null=True)
    ticket_type = models.CharField(max_length=100, choices=TICKET_TYPE_CHOICES, null=True)  # Add choices here

    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='In Progress')  # Updated field with choices

    detailed_summary = models.TextField(null=True)
    ticket_source = models.CharField(max_length=100, null=True)
    resolution = models.TextField(null=True)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="assigned_tickets")
    last_modified_by = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, related_name="modified_tickets")
    last_modified_at = models.DateTimeField(auto_now=True)
    contact_name = models.CharField(max_length=200, null=True)
    support_mode = models.CharField(max_length=100, choices=SUPPORT_MODE_CHOICES, null=True)  # Add choices here
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)
    due_date = models.DateTimeField(null=True, blank=True)  # New due date field
    proof_of_work = models.FileField(upload_to='proof_of_work/', null=True, blank=True)  # Proof of Work attachment field

    def __str__(self):
        return self.title


class MeetingRecord(models.Model):
    DoesNotExist = None
    objects = None
    record = models.ForeignKey(Record, on_delete=models.CASCADE, default=1)
    meeting_partner = models.CharField(max_length=255)
    products_discussed_partner = models.TextField()
    products_discussed_company = models.TextField()
    conclusion = models.TextField()
    follow_up_date = models.DateTimeField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    speaker = models.ForeignKey(User, related_name='speaker', on_delete=models.CASCADE, null=True)
    attendees = models.ManyToManyField(User, related_name='attendees')
    meeting_location = models.CharField(max_length=255, default='Virtual')

    def __str__(self):
        return f"Meeting with {self.meeting_partner} on {self.created_at}"


class PotentialLead(models.Model):
    company = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10, null=True)
    email = models.EmailField(null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    initial_comments = models.TextField(blank=True, null=True)  # Renamed field
    follow_up_date = models.DateTimeField(blank=True, null=True)
    conversation = models.TextField(blank=True, null=True)
    additional_comments = models.TextField(blank=True, null=True)

    objects = models.Manager()

    def __str__(self):
        return self.company

    def add_comment(self, user, comment_text):
        # Format: "username|timestamp|comment_text"
        comment = f"{user.username}|{timezone.now().isoformat()}|{comment_text}"
        if self.additional_comments:
            # Append the new comment to existing comments
            self.additional_comments += f"\n{comment}"
        else:
            self.additional_comments = comment
        self.save()

    def get_additional_comments(self):
        comments_list = []
        if self.additional_comments:
            for line in self.additional_comments.split('\n'):
                username, timestamp, text = line.split('|', 2)
                comments_list.append({
                    "user": username,
                    "timestamp": timezone.datetime.fromisoformat(timestamp),
                    "comment": text
                })
        return comments_list


class LeadComment(models.Model):
    objects = None
    lead = models.ForeignKey(PotentialLead, on_delete=models.CASCADE, related_name='lead_comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.lead.client_name}"


class UserSettings(models.Model):
    objects = None
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    side_panel_slide = models.BooleanField(default=False)
    notification_preferences = models.CharField(max_length=10, choices=[
        ('email', 'Email'),
        ('sms', 'SMS'),
        ('none', 'None')
    ], default='email')
    theme_selection = models.CharField(max_length=10, choices=[
        ('light', 'Light'),
        ('dark', 'Dark')
    ], default='light')

    def __str__(self):
        return f'{self.user.username} Settings'


class Profile(models.Model):
    objects = None
    user = models.OneToOneField(User, on_delete=models.CASCADE, unique=True)
    phone_number = models.CharField(max_length=15, blank=True)
    otp = models.CharField(max_length=6, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)  # Add the department field

    def __str__(self):
        return f'{self.user.username} Profile'


class Comment(models.Model):
    objects = None
    record = models.ForeignKey(Record, on_delete=models.CASCADE, related_name='comment_history')
    text = models.TextField()
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class DeletionHistory(models.Model):
    objects = None
    record_id = models.IntegerField(db_index=True)  # Indexing the record ID for faster lookup
    record_data = models.JSONField()  # Store all details of the record in JSON format
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    deleted_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        # Handle case where deleted_by could be None
        deleted_by_username = self.deleted_by.username if self.deleted_by else "Unknown"
        return f"Record {self.record_id} deleted by {deleted_by_username}"


class DeletedRecord(models.Model):
    objects = None
    record_id = models.IntegerField()
    client_name = models.CharField(max_length=255)
    company = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15)
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    deleted_by = models.ForeignKey(User, on_delete=models.SET_NULL, related_name='deleted_by', null=True)
    deleted_at = models.DateTimeField(auto_now_add=True)
    department = models.CharField(max_length=255, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    follow_up_date = models.DateTimeField(null=True, blank=True)
    remarks = models.TextField(null=True, blank=True)
    comments = models.TextField(null=True, blank=True)
    lead_source = models.CharField(max_length=255, null=True, blank=True)
    deletion_reason = models.TextField(null=True, blank=True)  # Allow deletion reason to be nullable

    def __str__(self):
        return f"{self.client_name} - Deleted"
