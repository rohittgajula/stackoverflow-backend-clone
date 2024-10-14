from rest_framework import serializers
from .models import User
from django.db import transaction

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        exclude = ['otp', 'password', 'groups', 'user_permissions']


class VerifyEmailSerializer(serializers.Serializer):
    otp = serializers.CharField()

class CreateUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        age = serializers.ReadOnlyField()
        
        model = User
        fields = ['first_name', 'last_name', 'username', 'email', 'password', 'date_of_birth', 'age']

    @transaction.atomic
    def create(self, validated_data):
        password = validated_data['password']
        user = User(**validated_data)
        if password:
            user.set_password(password)
        user.save()
        return user
    
    @transaction.atomic
    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        instance =  super().update(instance, validated_data)
        if password:
            instance.set_password(password)
        instance.save()
        return instance


