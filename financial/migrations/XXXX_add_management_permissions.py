from django.db import migrations

class Migration(migrations.Migration):
    dependencies = [
        ('financial', 'XXXX_previous_migration'),  # Replace with actual previous migration
    ]

    operations = [
        migrations.AlterModelOptions(
            name='financialaccount',
            options={
                'permissions': [
                    ('manage_accounts', 'Can manage financial accounts'),
                    ('manage_withdrawals', 'Can manage withdrawal requests'),
                ]
            },
        ),
    ] 