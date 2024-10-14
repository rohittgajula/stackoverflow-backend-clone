from rest_framework import serializers
from .models import Tag, Question, Answer, Comment


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ['tag_id', 'tag_title', 'tag_description']

class AllQuestionsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ['question_id', 'created_user', 'question_title', 'tags', 'views', 'comments_count', 'created_at']
        read_only_fields = ['created_user']

class CreateQuestionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Question
        fields = ['question_id', 'created_user', 'question_title', 'question_description', 'tags', 'views', 'votes_count', 'comments_count', 'created_at', 'updated_at']
        read_only_fields = ['question_id', 'created_user', 'views', 'votes_count', 'comments_count', 'created_at', 'updated_at']

class CreateAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Answer
        fields = ['answer_id', 'question', 'created_user', 'answer_description', 'comments_count', 'created_at', 'updated_at']
        read_only_fields = ['answer_id', 'question', 'created_user', 'comments_count', 'created_at', 'updated_at']


class CreateCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'question', 'answer', 'created_user', 'comment_description', 'created_at',]
        read_only_fields = ['comment_id', 'question', 'answer', 'created_user', 'created_at']

class AllCommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['comment_id', 'created_user', 'comment_description', 'created_at']
        read_only_fields = ['comment_id', 'created_user', 'created_at']

class AllAnswerSerializer(serializers.ModelSerializer):

    comments = AllCommentSerializer(many=True, read_only=True)
    class Meta:
        model = Answer
        fields = ['answer_id', 'created_user', 'answer_description', 'comments_count', 'created_at', 'updated_at', 'comments',]


class DetailQuestionView(serializers.ModelSerializer):

    answers = AllAnswerSerializer(many=True, read_only=True)
    comments = AllCommentSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ['question_id', 'created_user', 'question_title', 'question_description', 'tags', 'views', 'votes_count', 'comments_count', 'comments', 'created_at', 'updated_at', 'answers',]

