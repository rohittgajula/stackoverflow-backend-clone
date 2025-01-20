
from .models import Question

from django_elasticsearch_dsl.registries import registry
from django_elasticsearch_dsl import Document, Index, fields

@registry.register_document
class QuestionDocument(Document):
    class Index:
        name = 'questions'
        settings = {
            'number_of_shards':1,
            'number_of_replicas':0,
        }

    class Django:
        model = Question
        fields = ['question_title', 'question_description']

#   to push existing data into elastic search 
#           python3 manage.py search_index --rebuild