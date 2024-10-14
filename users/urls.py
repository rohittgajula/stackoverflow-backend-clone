from tkinter.font import names

from django.urls import path
from . import views

urlpatterns = [
    path("", views.all_users, name='all-users'),
    path("create/", views.create_user, name='create-user'),
    path("update/<str:pk>/", views.update_user, name='update-user'),
    path("delete/<str:pk>/", views.delete_user, name='delete-user'),
    path("verify/", views.verify_otp, name='verify-otp'),
    path("me/", views.current_user, name='current-user'),
]

