

from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.response import Response


def handle_not_found(model, identifier, id_value):
    try:
        obj = model.objects.get(**{identifier: id_value})
        return obj
    except model.DoesNotExist:
        return Response({
            'status':status.HTTP_404_NOT_FOUND,
            'message': f'{model} not found.'
        }, status.HTTP_404_NOT_FOUND)
    
