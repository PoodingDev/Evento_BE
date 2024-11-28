# Generated by Django 5.1.3 on 2024-11-28 14:08

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("calendars", "0003_remove_calendar_id_calendar_calendar_id"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name="Subscription",
            fields=[
                (
                    "subscription_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                (
                    "calendar_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="calendars.calendar",
                    ),
                ),
                (
                    "user_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to=settings.AUTH_USER_MODEL,
                    ),
                ),
            ],
        ),
    ]
