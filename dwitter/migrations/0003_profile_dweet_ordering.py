# Generated by Django 3.2.16 on 2022-12-12 23:22

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("dwitter", "0002_user_dweets"),
    ]

    operations = [
        migrations.AlterModelOptions(
            name="dweet",
            options={"ordering": ["-created_at"]},
        ),
        migrations.AlterModelOptions(
            name="profile",
            options={"ordering": ["user__username"]},
        ),
    ]