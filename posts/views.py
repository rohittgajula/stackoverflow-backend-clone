from django.shortcuts import get_object_or_404

from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework import mixins, generics

from .models import Tag, Question, Answer, Comment
from .serializers import ( TagSerializer, CreateQuestionSerializer, 
                          AllQuestionsSerializer, CreateAnswerSerializer, 
                          AllAnswerSerializer, CreateCommentSerializer, 
                          DetailQuestionView )

from .pagination import CustomPagination
from .tasks import send_answer_notification_mail
from .helper import handle_not_found

from django.core.cache import cache

import hashlib

from drf_yasg.utils import swagger_auto_schema

from .documents import QuestionDocument
from django_elasticsearch_dsl.search import Search

@api_view(['GET'])
@permission_classes([AllowAny])
def all_question(request):
    search_query = request.GET.get('search', None)      # get search parameters
    cached_questions = cache.get('all_questions')

    if search_query:
        search = QuestionDocument.search()
        search = search.query("multi_match",
                              query=search_query,
                              fields = ["question_title", "question_description"])
        search = search[:100]
        search_result = search.execute()

        # serialize search result
        questions = []
        for hit in search_result:
            question = {
                "id": hit.meta.id,
                "question_title":hit.question_title,
                "question_description":hit.question_description,
            }
            questions.append(question)

        cache_key = f'search_results_{search_query}'
        cache.set(cache_key, questions, timeout=600)
        data = questions

    elif not cached_questions:
        questions = Question.objects.all().order_by('created_at')
        serializer = AllQuestionsSerializer(questions, many=True)
        cache.set('all_questions', serializer.data, timeout=600)
        data = serializer.data
    else:
        data = cached_questions

    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(data, request)
    return paginator.get_paginated_response({
        'status':status.HTTP_200_OK,
        'message':'All questions' if not search_query else f'Search result for "{search_query}"',
        'data':result_page
    })


@swagger_auto_schema(method='POST', request_body=CreateAnswerSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_answer_for_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    data = request.data
    user = request.user

    serializer = CreateAnswerSerializer(data=data)
    if serializer.is_valid():
        serializer.save(created_user=user, question=question)
        send_answer_notification_mail.apply_async((question.created_user.email, question.question_title), countdown=90)
        return Response({
            'status':status.HTTP_201_CREATED,
            'message':f'Answer created for - {question.question_title}',
            'data':serializer.data
        }, status.HTTP_201_CREATED)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error.',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_answers_for_question(request, question_id):

    cache_key = hashlib.md5(f'{question_id}'.encode()).hexdigest()
    cache_data = cache.get(cache_key)

    if cache_data:
        return Response({
        'status':status.HTTP_200_OK,
        'message':f'Answers for question {question_id}',
        'data':cache_data
    }, status.HTTP_200_OK)
    
    try:
        question = Question.objects.get(question_id=question_id)
    except Question.DoesNotExist:
        return Response({
            'status':status.HTTP_404_NOT_FOUND,
            'message':f'Question {question_id} not found.'
        }, status.HTTP_404_NOT_FOUND)
    
    answers = question.answers.all()
    serializer = AllAnswerSerializer(answers, many=True)
    cache.set(cache_key, serializer.data, timeout=60)
    return Response({
        'status':status.HTTP_200_OK,
        'message':f'Answers for question {question_id}',
        'data':serializer.data
    }, status.HTTP_200_OK)


@swagger_auto_schema(method='PATCH', request_body=CreateAnswerSerializer)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_answer(request, answer_id):
    try:
        answer = Answer.objects.get(answer_id=answer_id)
    except Answer.DoesNotExist:
        return Response({
            'status':status.HTTP_404_NOT_FOUND,
            'message':'Answer not found.',
        }, status.HTTP_404_NOT_FOUND)
    
    if answer.created_user != request.user:
        return Response({
            'status':status.HTTP_401_UNAUTHORIZED,
            'message':'You are not allowed to update this answer.'
        }, status.HTTP_401_UNAUTHORIZED)
    
    data = request.data
    
    serializer = CreateAnswerSerializer(answer, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status':status.HTTP_202_ACCEPTED,
            'message':'Answer updated.',
            'data':serializer.data
        }, status.HTTP_202_ACCEPTED)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error.',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)
    

@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_answer(request, answer_id):
    try:
        answer = Answer.objects.get(answer_id=answer_id)
    except Answer.DoesNotExist:
        return Response({
            'status':status.HTTP_404_NOT_FOUND,
            'message':f'Answer not found with id {answer_id}.',
        }, status.HTTP_404_NOT_FOUND)
    
    if request.user != answer.created_user:
        return Response({
            'status':status.HTTP_401_UNAUTHORIZED,
            'message':'You are not allowed to perform this action.',
        }, status.HTTP_401_UNAUTHORIZED)
    
    answer.delete()
    return Response({
        'status':status.HTTP_200_OK,
        'message':f'Answer deleted with id {answer_id}'
    }, status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([AllowAny])
def detail_question_view(request, question_id):

    cache_key = f'detail_question_{question_id}'

    question = get_object_or_404(Question, question_id=question_id)
    question.views += 1
    question.save()

    cached_data = cache.get(cache_key)

    if cached_data:
        cached_data['views'] = question.views
        cache.set(cache_key, cached_data, timeout=600)

        return Response({
        'status':status.HTTP_200_OK,
        'message':f'Question {question_id}.',
        'data':cached_data
    }, status.HTTP_200_OK)

    serializer = DetailQuestionView(question)
    cache.set(cache_key, serializer.data, timeout=600)
    return Response({
        'status':status.HTTP_200_OK,
        'message':f'Question {question_id}.',
        'data':serializer.data
    }, status.HTTP_200_OK)


@swagger_auto_schema(method='POST', request_body=CreateQuestionSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_question(request):
    data = request.data
    user = request.user

    data = {**data}
    data.pop('created_user', None)

    serializer = CreateQuestionSerializer(data=data)
    if serializer.is_valid():
        question = serializer.save(created_user = user)
        return Response({
            'status':status.HTTP_201_CREATED,
            'message':'Question created.',
            'data':CreateQuestionSerializer(question).data
        }, status.HTTP_201_CREATED)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)


@swagger_auto_schema(method='PATCH', request_body=CreateQuestionSerializer)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_question(request, question_id):
    data = request.data
    user = request.user

    question = get_object_or_404(Question, question_id=question_id)

    if user != question.created_user:
        return Response({
            'status':status.HTTP_401_UNAUTHORIZED,
            'message':'You are not allowed to update this question.'
        }, status.HTTP_401_UNAUTHORIZED)
    
    serializer = CreateQuestionSerializer(instance=question, data=data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status':status.HTTP_202_ACCEPTED,
            'message':'Question update successful.',
            'data':serializer.data
        }, status.HTTP_202_ACCEPTED)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)
    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated, IsAdminUser])
def delete_question(request, question_id):
    try:
        question = Question.objects.get(question_id=question_id)
    except Question.DoesNotExist:
        return Response({
            'status':status.HTTP_404_NOT_FOUND,
            'message':'No question found.'
        }, status.HTTP_404_NOT_FOUND)
    
    user = request.user

    if question.created_user != user:
        return Response({
            'status':status.HTTP_401_UNAUTHORIZED,
            'message':'You cannot delete this question',
        }, status.HTTP_401_UNAUTHORIZED)
    else:
        question.delete()
        cache.delete('all_questions')
        return Response({
            'status':status.HTTP_200_OK,
            'message':'Question deleted successfully.',
        }, status.HTTP_200_OK)
    

@swagger_auto_schema(method='POST', request_body=CreateCommentSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment_for_question(request, question_id):
    question = get_object_or_404(Question, question_id=question_id)
    data = request.data

    serializer = CreateCommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(question=question, created_user=request.user)

        question.comments_count += 1
        question.save()

        return Response({
            'status':status.HTTP_200_OK,
            'message':'Comment created successfully.',
            'data':serializer.data
        }, status.HTTP_200_OK)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error.',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(method='POST', request_body=CreateCommentSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment_for_answer(request, answer_id):
    answer = get_object_or_404(Answer, answer_id=answer_id)
    data = request.data

    serializer = CreateCommentSerializer(data=data)
    if serializer.is_valid():
        serializer.save(answer=answer, created_user=request.user)

        answer.comments_count += 1
        answer.save()

        return Response({
            'status':status.HTTP_200_OK,
            'message':'Comment created successfully.',
            'data':serializer.data
        }, status.HTTP_200_OK)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error.',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)

    
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def delete_comment(request, comment_id):
    comment = get_object_or_404(Comment, comment_id=comment_id)
    user = request.user

    if user != comment.created_user:
        return Response({
            'status':status.HTTP_401_UNAUTHORIZED,
            'message':'You are not allowed to delete this comment.'
        }, status.HTTP_401_UNAUTHORIZED)
    
    comment.delete()

    question = comment.question
    answer = comment.answer
    if comment.question != None:
        question.comments_count -= 1
        question.save()
    else:
        answer.comments_count -= 1
        answer.save()

    return Response({
        'status':status.HTTP_200_OK,
        'message':'Comment deleted successfully',
    }, status.HTTP_200_OK)
    

@swagger_auto_schema(method='POST', request_body=TagSerializer)
@api_view(['POST'])
@permission_classes([IsAdminUser])
def create_tag(request):
    data = request.data
    serializer = TagSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response({
            'status':status.HTTP_201_CREATED,
            'message':'Tag created.',
            'data':serializer.data
        }, status.HTTP_201_CREATED)
    else:
        return Response({
            'status':status.HTTP_400_BAD_REQUEST,
            'message':'Validation error',
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([AllowAny])
def all_tags(request):

    cached_data = cache.get('all_tags')

    if cached_data:
        return Response({
        'status':status.HTTP_200_OK,
        'message':'All tags.',
        'data':cached_data
    }, status.HTTP_200_OK)

    tags = Tag.objects.all().order_by('tag_id')
    serializer = TagSerializer(tags, many=True)
    cache.set('all_tags', serializer.data, timeout=600)
    return Response({
        'status':status.HTTP_200_OK,
        'message':'All tags.',
        'data':serializer.data
    }, status.HTTP_200_OK)


@api_view(['DELETE'])
@permission_classes([IsAdminUser])
def delete_tag(request, tag_id):
    try:
        tag = Tag.objects.get(tag_id=tag_id)
        tag.delete()
        return Response({
            'status':status.HTTP_200_OK,
            'message':'Tag deleted successfully.',
            'data':tag.tag_title
        }, status.HTTP_200_OK)
    except Tag.DoesNotExist:
        return Response({
            'status':status.HTTP_404_NOT_FOUND,
            'message':'Tag not found.',
        }, status.HTTP_404_NOT_FOUND)




