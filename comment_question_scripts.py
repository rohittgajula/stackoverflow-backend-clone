import os
import csv
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stackoverflow.settings')
django.setup()

from posts.models import Comment, Question
from users.models import User


def load_comment_for_question_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f'File {file_path} does not exist.')
        return
    
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            comments = []

            for row in reader:
                comment_description = row.get('comment_description')
                question_id = row.get('question')
                created_user_id = row.get('created_user')

                if not comment_description:
                    print(f'Skipping the row with missing comment at row : {row}')
                    continue

                try:
                    question = Question.objects.get(question_id=question_id.strip())
                except Question.DoesNotExist:
                    print(f'Question with ID {question_id} does not exist.')
                    continue

                try:
                    created_user = User.objects.get(id=created_user_id.strip())
                except User.DoesNotExist:
                    print(f'User with user ID {created_user_id} does not exist.')
                    continue

                comment = Comment(
                    comment_description=comment_description,
                    question=question,
                    created_user=created_user,
                    answer=None
                )
                comments.append(comment)
            
            Comment.objects.bulk_create(comments)
            print(f'Successfully updated {len(comments)} comments.')

    except Exception as e:
        print(f'An error occurred : {e}')


if __name__ == "__main__":
    csv_file_path = "comment_question_data.csv"
    load_comment_for_question_from_csv(csv_file_path)

