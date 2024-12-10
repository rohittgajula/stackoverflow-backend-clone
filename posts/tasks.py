
from django.core.mail import send_mail

from celery import shared_task
from django.conf import settings


@shared_task
def send_answer_notification_mail(email, question_title):
    print(f'sending notification mail to {email}')
    subject = "Stackoverflow clone."
    message = f'Someone answered your question - {question_title}.'
    email_from = settings.EMAIL_HOST_USER
    try:
        send_mail(subject, message, email_from, [email])
        print(f'Notification mail sent to {email}')
    except Exception as e:
        print(f'Failed to send mail to {email}. Error : {e}')

