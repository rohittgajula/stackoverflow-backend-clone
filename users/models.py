from email.policy import default

from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

from datetime import date


class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password, **extra_fields):
        if username is None:
            raise ValueError("Username is required.")
        if email is None:
            raise ValueError("Email is required.")
        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.is_active = True
        user.save(using=self._db)
        return user
    
    def create_superuser(self, username, email, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_superuser", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("is_staff must be true.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("is_superuser must be true.")
        
        user = self.create_user(username=username, email=email, password=password, **extra_fields)
        return user

class User(AbstractBaseUser, PermissionsMixin):
    id = models.BigAutoField(primary_key=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    username = models.CharField(max_length=150 ,blank=False, null=False, unique=True, db_index=True)
    email = models.EmailField(unique=True, db_index=True)
    otp = models.CharField(max_length=6, null=True, blank=True)
    score = models.IntegerField(blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    age = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_superuser = models.BooleanField(default=False)


    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = CustomUserManager()

    def __str__(self):
        return f'{self.username} - {self.email}'

