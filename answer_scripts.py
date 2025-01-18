import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stackoverflow.settings')
django.setup()

from posts.models import Answer, Question
from users.models import User


def load_answer_data_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f"File {file_path} does not exist.")
        return

    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            answers = []

            for row in reader:
                answer_description = str(row.get('answer_description'))
                question_id = row.get('question')
                created_user_id = row.get('created_user')
                comments_count = int(row.get('comments_count', 0))

                if not answer_description:
                    print(f"Skipping row with missing answer description: {row}")
                    continue

                try:
                    created_user = User.objects.get(id=created_user_id.strip())
                except User.DoesNotExist:
                    print(f"User with ID {created_user_id} does not exist. Skipping row: {row}")
                    continue

                try:
                    question = Question.objects.get(question_id=question_id.strip())
                except Question.DoesNotExist:
                    print(f"Question with ID {question_id} does not exist. Skipping row: {row}")
                    continue

                answer = Answer(
                    answer_description=answer_description,
                    question=question,
                    created_user=created_user,
                    comments_count=comments_count,
                )
                answers.append(answer)

            Answer.objects.bulk_create(answers)
            print(f"Successfully updated {len(answers)} answers.")

    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    csv_file_path = "answer_data.csv"
    load_answer_data_from_csv(csv_file_path)
