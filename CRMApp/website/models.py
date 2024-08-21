from django.core.validators import RegexValidator
from django.db import models
from django.contrib.auth.models import User


class Record(models.Model):
    DoesNotExist = None
    objects = None
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.CharField(max_length=50)
    client_name = models.CharField(max_length=50)
    dept_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10,
                             validators=[RegexValidator(r'^\d{10}$', message="Phone number must be 10 digits.")])
    email = models.EmailField(max_length=100)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_leads', null=True,
                                    blank=True)
    last_modified_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='modified_records', null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    comments = models.CharField(max_length=200)
    remarks = models.CharField(max_length=200)
    visible_to = models.ManyToManyField(User, related_name='visible_tickets', blank=True)
    attachments = models.FileField(upload_to='attachments/', null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_records', null=True)
    social_media_details = models.TextField(null=True, blank=True)
    CLASSIFICATION_CHOICES = (
        ('assigned', 'Assigned'),
        ('unassigned', 'Unassigned'),
        ('dead', 'Dead'),
        ('in_progress', 'In Progress'),
    )
    classification = models.CharField(max_length=20, choices=CLASSIFICATION_CHOICES, default='unassigned')
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
    lead_source = models.CharField(max_length=50, choices=LEAD_SOURCE_CHOICES, blank=True, null=True)

    def __str__(self):
        return f"{self.company} - {self.client_name}"

    class Meta:
        indexes = [
            models.Index(fields=['assigned_to']),
            models.Index(fields=['created_at']),
        ]


class NotificationManager(models.Manager):
    def unread_for_user(self, user):
        return self.filter(user=user, is_read=False)


class Notification(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    objects = NotificationManager()

    def __str__(self):
        return 'Notification for {self.user.username}: {self.message}'

    def mark_as_read(self):
        self.is_read = True
        self.save()


class Ticket(models.Model):
    objects = None
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    modified_at = models.DateTimeField(auto_now=True)
    company_name = models.CharField(max_length=200, null=True)
    ticket_type = models.CharField(max_length=100, null=True)
    status = models.CharField(max_length=50)
    account_name = models.CharField(max_length=200, null=True)
    detailed_summary = models.TextField(null=True)
    comments_history = models.TextField(null=True)
    contract = models.CharField(max_length=200, null=True)
    ticket_source = models.CharField(max_length=100, null=True)
    resolution = models.TextField(null=True)
    contact_name = models.CharField(max_length=200, null=True)
    support_mode = models.CharField(max_length=100, null=True)
    phone = models.CharField(max_length=20, null=True)
    email = models.EmailField(null=True)

    def __str__(self):
        return self.title


class MeetingRecord(models.Model):
    objects = None
    record = models.ForeignKey(Record, on_delete=models.CASCADE, default=1)
    meeting_partner = models.CharField(max_length=255)
    products_discussed_partner = models.TextField()
    products_discussed_company = models.TextField()
    conclusion = models.TextField()
    follow_up_date = models.DateField(null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    speaker = models.ForeignKey(User, related_name='speaker', on_delete=models.CASCADE, null=True)
    attendees = models.ManyToManyField(User, related_name='attendees')
    meeting_location = models.CharField(max_length=255, default='Virtual')

    def __str__(self):
        return f"Meeting with {self.meeting_partner} on {self.created_at}"


class PotentialLead(models.Model):
    objects = None
    company = models.CharField(max_length=255)
    client_name = models.CharField(max_length=255)
    phone = models.CharField(max_length=10)
    email = models.EmailField()
    created_by = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    comments = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.company


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

    def __str__(self):
        return f'{self.user.username} Profile'
