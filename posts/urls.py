from django.urls import path
from . import views


urlpatterns = [
    path("questions/", views.all_question, name='all_questions'),
    path("question/create/", views.create_question, name='create_question'),
    path("question/<str:question_id>/update/", views.update_question, name='update_question'),
    path("question/<str:question_id>/delete/", views.delete_question, name='delete_question'),

    path("question/<str:question_id>/detail/", views.detail_question_view, name='detail_question_view'),

    path("question/<str:question_id>/answers/", views.get_answers_for_question, name='all_answers_for_question'),
    path("question/<str:question_id>/answer/create/", views.create_answer_for_question, name='create_answer'),
    path("answer/<str:answer_id>/update/", views.update_answer, name='update_answer'),
    path("answer/<str:answer_id>/delete/", views.delete_answer, name='delete_answer'),

    path("comment/question/<str:question_id>/create/", views.create_comment_for_question, name='create_comment_for_question'),
    path("comment/answer/<str:answer_id>/create/", views.create_comment_for_answer, name='create_comment_for_answer'),
    path("comment/<str:comment_id>/delete/", views.delete_comment, name='delete_comment'),

    # admin user can perform this actions.
    path("tags/", views.all_tags, name='all_tags'),
    path("tags/create/", views.create_tag, name='create_tag'),
    path("tags/delete/<str:tag_id>/", views.delete_tag, name='delete_tag'),
]

