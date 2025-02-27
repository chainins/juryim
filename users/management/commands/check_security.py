from django.core.management.base import BaseCommand
from users.models import User, SecurityQuestion

class Command(BaseCommand):
    help = 'Check security questions for users'

    def handle(self, *args, **options):
        users = User.objects.all()
        for user in users:
            questions = SecurityQuestion.objects.filter(user=user)
            self.stdout.write(f"User: {user.username}")
            if questions.exists():
                for q in questions:
                    self.stdout.write(f"  Question: {q.question}")
                    self.stdout.write(f"  Answer: {q.answer}")
            else:
                self.stdout.write("  No security questions found") 