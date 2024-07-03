from django.db import models
from django.contrib.auth.models import User


class Record(models.Model):
    objects = None
    created_at = models.DateTimeField(auto_now_add=True)
    company = models.CharField(max_length=50)
    client_name = models.CharField(max_length=50)
    dept_name = models.CharField(max_length=50)
    phone = models.CharField(max_length=10)
    email = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    address = models.CharField(max_length=200)
    assigned_to = models.ForeignKey(User, on_delete=models.CASCADE, related_name='assigned_leads', null=True, blank=True)
    follow_up_date = models.DateField(null=True, blank=True)
    comments = models.CharField(max_length=200)
    remarks = models.CharField(max_length=200)
    visible_to = models.ManyToManyField(User, related_name='visible_leads', blank=True)

    def __str__(self):
        return f"{self.client_name} from {self.company}"


class Notification(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return 'Notification for {self.user.username}'


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
