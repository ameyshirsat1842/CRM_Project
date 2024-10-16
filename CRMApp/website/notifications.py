from django.core.mail import send_mail
from django.conf import settings


def send_notification_to_user(user, message):
    subject = "Notification from Tecstaq Lead Management"
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [user.email],
        fail_silently=False,
    )
