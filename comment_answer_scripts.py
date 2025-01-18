import os
import csv
import django


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stackoverflow.settings')
django.setup()

from posts.models import Comment, Answer
from users.models import User


def load_comment_for_answers_from_csv(file_path):
    if not os.path.exists(file_path):
        print(f'File path {file_path} does not exists.')
        return
    
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            comments = []

            for row in reader:
                comment_description = row.get('comment_description')
                answer_id = row.get('answer')
                created_user_id = row.get('created_user')

                if not comment_description:
                    print(f'Skipping the row with missing comment on row : {row}')
                    continue

                try:
                    answer = Answer.objects.get(answer_id=answer_id.strip())
                except Answer.DoesNotExist:
                    print(f'Answer with answer_id {answer_id} does not exist.')
                    continue

                try:
                    created_user = User.objects.get(id=created_user_id.strip())
                except User.DoesNotExist:
                    print(f'User with user ID {created_user_id} does not exist.')
                    continue

                comment = Comment(
                    comment_description=comment_description,
                    answer=answer,
                    created_user=created_user,
                    question=None
                )
                comments.append(comment)
            
            Comment.objects.bulk_create(comments)
            print(f'Successfully created {len(comments)} comments.')


    except Exception as e:
        print(f'An error occurred as : {e}')


if __name__ == "__main__":
    csv_file_path = "comment_answer_data.csv"
    load_comment_for_answers_from_csv(csv_file_path)

    