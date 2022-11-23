# Generated by Django 3.2.16 on 2022-11-21 22:57

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("dwitter", "0001_user_profiles"),
    ]

    operations = [
        migrations.CreateModel(
            name="Dweet",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("body", models.CharField(max_length=140)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.DO_NOTHING,
                        related_name="dweets",
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
