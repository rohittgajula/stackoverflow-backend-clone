from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from django.utils import timezone
from .models import User
from django.core.cache import cache
from django.db import transaction


@receiver(post_save, sender=User)
def calculate_age(sender, instance, created, **kwargs):
    if instance.date_of_birth:
        today = timezone.now().date()
        age = today.year - instance.date_of_birth.year - (
            (today.month, today.day) < (instance.date_of_birth.month, instance.date_of_birth.day)
        )
        if instance.age != age:
            instance.age = age
            with transaction.atomic():
                instance.save(update_fields=['age'])
    else:
        instance.age = None

@receiver(post_save, sender=User)
def clear_user_cache_on_create(sender, instance, created, **kwargs):
    if created:
        cache.delete('all_users')

@receiver(post_delete, sender=User)
def clear_user_cache_on_delete(sender, instance, **kwargs):
    cache.delete('all_users')

