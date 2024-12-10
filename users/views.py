from django.shortcuts import get_object_or_404
from rest_framework import status

from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny

from .tasks import send_otp_via_mail, expire_otp_timer
from .serializers import UserSerializer, CreateUpdateSerializer, VerifyEmailSerializer
from .models import User
from .pagination import CustomPagination

from django.core.cache import cache

from django.db import transaction

from drf_yasg.utils import swagger_auto_schema


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def current_user(request):
    user = request.user
    serializer = UserSerializer(user)
    return Response({
        'status':200,
        'user':serializer.data
    }, status.HTTP_200_OK)
    

@api_view(['GET'])
@permission_classes([IsAdminUser])
def all_users(request):

    cached_users = cache.get('all_users')

    if not cached_users:
        users = User.objects.all().order_by('created_at')
        serializer = UserSerializer(users, many=True)
        cache.set('all_users', serializer.data, timeout=600)
        data = serializer.data
    else:
        data = cached_users
    
    paginator = CustomPagination()
    result_page = paginator.paginate_queryset(data, request)
    return paginator.get_paginated_response({
        'status':status.HTTP_200_OK,
        'message':'All users.',
        'users':result_page
    })

@swagger_auto_schema(method='POST', request_body=CreateUpdateSerializer)
@api_view(['POST'])
@permission_classes([AllowAny])
def create_user(request):
    data = request.data
    serializer = CreateUpdateSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        send_otp_via_mail.delay(serializer.validated_data['email'])
        expire_otp_timer.apply_async((serializer.validated_data['email'],), countdown=3600)
        return Response({
            'status':201,
            'data':serializer.data
        }, status.HTTP_201_CREATED)
    else:
        return Response({
            'status':400,
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)
    
@swagger_auto_schema(method='POST', request_body=VerifyEmailSerializer)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_otp(request):
    data = request.data
    user = request.user

    serializer = VerifyEmailSerializer(data=data)
    if serializer.is_valid():
        print("User OTP:", user.otp)
        print("Serializer OTP:", serializer.data['otp'])
        if user.otp != serializer.data['otp']:
            return Response({
                'status':400,
                'error':'Wrong otp.'
            }, status.HTTP_400_BAD_REQUEST)
        else:
            user.is_verified = True
            user.save()
            return Response({
                'status':202,
                'message':f'{user.email} verified.'
            }, status.HTTP_202_ACCEPTED)
    else:
        return Response({
            'status':400,
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)
    

@swagger_auto_schema(method='PATCH', request_body=CreateUpdateSerializer)
@api_view(['PATCH'])
def update_user(request, pk):
    user = get_object_or_404(User, id=pk)

    if request.user != user:
        return Response({
            'status':403,
            'error':'You do not have permission to update this profile.'
        }, status.HTTP_403_FORBIDDEN)

    data = request.data

    serializer = CreateUpdateSerializer(user, data=data, partial=True)

    if serializer.is_valid():
        serializer.save()
        return Response({
            'status':200,
            'data':serializer.data
        }, status.HTTP_200_OK)
    else:
        return Response({
            'status':400,
            'error':serializer.errors
        }, status.HTTP_400_BAD_REQUEST)
    
    
@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_user(request, pk):
    user = get_object_or_404(User, id=pk)
    print(user, request.user)

    if request.user != user:
        return Response({
            'status':403,
            'error':'You do not have permission to delete this profile.'
        }, status.HTTP_403_FORBIDDEN)
    
    user.delete()
    return Response({
        'status':200,
        'data':f'{user.email} deleted sucessfully.'
    }, status.HTTP_200_OK)



