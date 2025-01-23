
from locust import HttpUser, task, between

import random

class LoadTesterUser(HttpUser):
    wait_time = between(1,5)

    @task
    def load_main_page(self):
        self.client.get('/')

    @task
    def all_questions(self):
        self.client.get('/api/questions/')

    @task
    def get_question(self):
        question_id = random.randint(1, 800)
        self.client.get(f'/api/question/{question_id}/detail/')

    @task
    def get_tags(self):
        self.client.get('/api/tags/')

    @task
    def get_answer_for_question(self):
        question_id = random.randint(1, 1000)
        self.client.get(f'/question/{question_id}/answers/')

