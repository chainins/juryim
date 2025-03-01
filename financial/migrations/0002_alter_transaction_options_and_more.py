# Generated by Django 4.2.17 on 2025-02-08 04:50

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("financial", "0001_initial"),
    ]

    operations = [
        migrations.AlterModelOptions(name="transaction", options={},),
        migrations.AlterModelOptions(name="withdrawalrequest", options={},),
        migrations.AlterModelTable(name="transaction", table=None,),
        migrations.AlterModelTable(name="withdrawalrequest", table=None,),
        migrations.CreateModel(
            name="DepositRequest",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("amount", models.DecimalField(decimal_places=8, max_digits=18)),
                (
                    "transaction_hash",
                    models.CharField(blank=True, max_length=100, null=True),
                ),
                (
                    "status",
                    models.CharField(
                        choices=[
                            ("pending", "Pending"),
                            ("approved", "Approved"),
                            ("rejected", "Rejected"),
                        ],
                        default="pending",
                        max_length=20,
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("processed_at", models.DateTimeField(blank=True, null=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
