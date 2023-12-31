# Generated by Django 5.0 on 2023-12-21 06:44

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Master",
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
                ("Email", models.EmailField(max_length=254, null=True, unique=True)),
                ("Password", models.CharField(max_length=20, null=True)),
            ],
        ),
        migrations.CreateModel(
            name="UserProfile",
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
                ("FullName", models.CharField(default="", max_length=25, null=True)),
                ("Mobile", models.CharField(default="", max_length=10, null=True)),
                (
                    "Master",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE, to="quizApp.master"
                    ),
                ),
            ],
        ),
    ]
