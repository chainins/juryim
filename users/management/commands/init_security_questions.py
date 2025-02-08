from django.core.management.base import BaseCommand
from users.models import SecurityQuestion

class Command(BaseCommand):
    help = 'Initialize default security questions'

    def handle(self, *args, **kwargs):
        default_questions = [
            "What was the name of your first pet?",
            "In which city were you born?",
            "What was your childhood nickname?",
            "What is your mother's maiden name?",
            "What was the name of your first school?",
            "What was your favorite food as a child?",
            "What was the model of your first car?",
            "What is the name of your favorite childhood teacher?",
            "What is your favorite book?",
            "What is the name of the street you grew up on?",
            # Add more default questions here
        ]

        created_count = 0
        for question in default_questions:
            _, created = SecurityQuestion.objects.get_or_create(
                question_text=question,
                is_custom=False
            )
            if created:
                created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} security questions'
            )
        ) 