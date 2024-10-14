from django.db.models.signals import post_save, post_delete
from django.core.cache import cache
from django.dispatch import receiver

from .models import Question, Answer, Comment, Tag
import hashlib


@receiver([post_save, post_delete], sender=Question)
def clear_question_cache(sender, instance, **kwargs):
    cache_key = hashlib.md5(f'{instance.question_id}'.encode()).hexdigest()
    cache.delete(cache_key)

@receiver([post_save, post_delete], sender=Answer)
def clear_answer_cache(sender, instance, **kwargs):
    question_id = instance.question.question_id
    cache_key = hashlib.md5(f'{question_id}'.encode()).hexdigest()
    cache.delete(cache_key)


@receiver([post_save, post_delete], sender=Comment)
def clear_comment_cache(sender, instance, **kwargs):
    question_id = instance.question.question_id
    cache_key = hashlib.md5(f'{question_id}'.encode()).hexdigest()
    cache.delete(cache_key)


@receiver(post_save, sender=Question)
def clear_question_cache_on_create(sender, instance, created, **kwargs):
    if created:
        cache.delete('all_questions')

@receiver(post_delete, sender=Question)
def clear_question_cache_on_delete(sender, instance, **kwargs):
    cache.delete('all_questions')

@receiver(post_save, sender=Tag)
def clear_tag_cache_on_save(sender, instance, created, **kwargs):
    if created:
        cache.delete('all_tags')

@receiver(post_delete, sender=Tag)
def clear_tag_cache_on_delete(sender, instance, **kwargs):
    cache.delete('all_tags')

