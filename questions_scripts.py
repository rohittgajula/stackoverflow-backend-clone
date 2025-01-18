import os
import csv
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stackoverflow.settings')
django.setup()

from posts.models import Question, Tag
from users.models import User

def load_question_data_from_csv(file_path):

    if not os.path.exists(file_path):
        print(f'File {file_path} does not exist.')
        return
    
    try:
        with open(file_path, 'r') as csvfile:
            reader = csv.DictReader(csvfile)
            questions = []

            for row in reader:
                question_title = row.get('question_title')
                question_description = row.get('question_description')
                tags = row.get('tags')
                created_user_id = row.get('created_user')  # This should be the User ID now
                views = row.get('views', 0)  # Default to 0 if not present in CSV
                votes_count = row.get('votes_count', 0)  # Default to 0 if not present in CSV
                comments_count = row.get('comments_count', 0)  # Default to 0 if not present in CSV

                if not question_title or not question_description:
                    print(f'Skipping row with missing data: {row}')
                    continue
                

                # THIS IS FOR MANY-TO-MANY ONLY
                # Process the tags field (assuming tags are comma-separated)
                tag_list = tags.split(',') if tags else []

                # Retrieve or create tags
                tag_objects = []
                for tag_name in tag_list:
                    tag_name = tag_name.strip()  # Clean up any extra spaces
                    tag, created = Tag.objects.get_or_create(tag_title=tag_name)
                    tag_objects.append(tag)

                # Retrieve the user who created the question (by their user ID)
                created_user = None
                if created_user_id:
                    try:
                        created_user = User.objects.get(id=created_user_id.strip())
                    except User.DoesNotExist:
                        print(f"User with ID {created_user_id} does not exist. Skipping this row.")
                        continue
                else:
                    print(f"No 'created_user' found for row: {row}. Skipping this row.")
                    continue

                # Create the Question object
                question = Question(
                    question_title=question_title,
                    question_description=question_description,
                    created_user=created_user,  # Assign the user here
                    views=views,  # Assign views count
                    votes_count=votes_count,  # Assign votes count
                    comments_count=comments_count  # Assign comments count
                )
                questions.append(question)

                # Save the question and set the many-to-many relationship for tags
                question.save()
                question.tags.set(tag_objects)

            print(f'Successfully updated {len(questions)} questions.')

    except Exception as e:
        print(f'An error occurred: {e}')

if __name__ == "__main__":
    csv_file_path = "question_data.csv"  # Make sure to provide the correct path
    load_question_data_from_csv(csv_file_path)
