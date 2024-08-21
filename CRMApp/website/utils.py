import random
from django.core.mail import send_mail


def generate_otp():
    return random.randint(100000, 999999)


def send_otp_to_email(user):
    otp = generate_otp()
    user.profile.otp = otp  # Assuming you have an OTP field in the profile model
    user.profile.save()

    send_mail(
        'OTP for Tecstaq Lead Management',
        f'Your OTP code is {otp}',
        'no-reply@yourdomain.com',
        [user.email],
        fail_silently=False,
    )


def verify_otp(user, otp):
    return str(user.profile.otp) == otp  # Verify OTP
