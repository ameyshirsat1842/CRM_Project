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
    assigned_person = models.CharField(max_length=50)
    follow_up_date = models.DateField(null=True, blank=True)
    comments = models.CharField(max_length=200)

    def __str__(self):
        return "{self.client_name}"


class Notification(models.Model):
    objects = None
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return 'Notification for {self.user.username}'

