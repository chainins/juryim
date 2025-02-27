from django.db import migrations

def add_security_questions(apps, schema_editor):
    User = apps.get_model('users', 'User')
    SecurityQuestion = apps.get_model('users', 'SecurityQuestion')
    
    # Add security questions for all users that don't have one
    for user in User.objects.all():
        if not SecurityQuestion.objects.filter(user=user).exists():
            SecurityQuestion.objects.create(
                user=user,
                question="What is your favorite color?",
                answer="blue"  # Default answer for testing
            )

class Migration(migrations.Migration):
    dependencies = [
        ('users', '0001_initial'),  # Replace with your last migration
    ]

    operations = [
        migrations.RunPython(add_security_questions),
    ] 