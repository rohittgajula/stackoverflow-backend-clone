

from celery import shared_task
from django.conf import settings
from .models import User
import random

from django.shortcuts import get_object_or_404
from django.core.mail import send_mail


@shared_task
def send_otp_via_mail(email):
    print("Task started.")
    subject = "Stackoverflow-clone verification mail."
    otp = random.randint(100000, 999999)
    message = f'Your verification otp is : {otp}, expires in 10min.'
    email_from = settings.EMAIL_HOST_USER
    try:
        print(f"Sending email to {email} from {email_from}")
        send_mail(subject, message, email_from, [email])

        user_obj = User.objects.get(email=email)
        user_obj.otp = otp
        user_obj.save()
        print(f'Email successfully sent to {email}')
    except Exception as e:
        print(f'Failed to send email to {email}. Error : {str(e)}')


@shared_task
def expire_otp_timer(email):
    try:
        print(f'OTP expiration task started for {email}, expires in 10min.')
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        print("User not found.")
        return
    
    user.otp = None
    user.save()
    print(f'otp removed for {email}')

