from django.db import models
from users.models import User


VOTE_CHOICE = (
    (1, 'Upvote'),
    (-1, 'Downvote')
)

class Tag(models.Model):
    tag_id = models.AutoField(primary_key=True)
    tag_title = models.CharField(max_length=20, unique=True)
    tag_description = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return str(f'{self.tag_id} - {self.tag_title}')
    
class Question(models.Model):
    question_id = models.AutoField(primary_key=True, unique=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='questions')
    question_title = models.CharField(max_length=150, blank=False, null=False)
    question_description = models.TextField(blank=False, null=False)
    tags = models.ManyToManyField(Tag, related_name='questions')
    views = models.IntegerField(default=0)
    votes_count = models.IntegerField(default=0)
    comments_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f'{self.question_title} - {self.created_user.email} - {self.question_id}')
    
class Answer(models.Model):
    answer_id = models.AutoField(primary_key=True, unique=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='answers')
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='answers')
    answer_description = models.TextField()
    comments_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(f'{self.question.question_title} - {self.answer_id} - {self.created_user.email}')


class Comment(models.Model):
    comment_id = models.AutoField(primary_key=True)
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='comments', null=True, blank=True)
    created_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='commants')
    comment_description = models.CharField(max_length=150, blank=False, null=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(f'Created by : {self.created_user.email}')
    
class Vote(models.Model):
    vote_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='votes')
    question = models.ForeignKey(Question, on_delete=models.CASCADE, related_name='votes')
    answer = models.ForeignKey(Answer, on_delete=models.CASCADE, related_name='votes')
    vote_type = models.SmallIntegerField(choices=VOTE_CHOICE)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'question'), ('user', 'answer'))

    def save(self, *args, **kwargs):
        
        if self.question:
            self.question.votes_count = sum(v.vote_type for v in self.question.votes.all())
            self.question.save()
        elif self.answer:
            self.answer.votes_count = sum(v.vote_type for v in self.answer.votes.all())
            self.answer.save()
        super().save(*args, **kwargs)
