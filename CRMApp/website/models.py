from django.db import models


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
        return f"{self.client_name}"
