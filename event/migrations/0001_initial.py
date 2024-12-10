# Generated by Django 5.1.3 on 2024-12-10 03:05

import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Event",
            fields=[
                (
                    "event_id",
                    models.UUIDField(
                        default=uuid.uuid4,
                        editable=False,
                        primary_key=True,
                        serialize=False,
                    ),
                ),
                ("title", models.CharField(max_length=255, verbose_name="이벤트 제목")),
                (
                    "description",
                    models.TextField(blank=True, null=True, verbose_name="이벤트 설명"),
                ),
                ("start_time", models.DateTimeField(verbose_name="시작 시간")),
                ("end_time", models.DateTimeField(verbose_name="종료 시간")),
                (
                    "is_public",
                    models.BooleanField(default=False, verbose_name="공개 여부"),
                ),
                (
                    "location",
                    models.CharField(
                        blank=True, max_length=255, null=True, verbose_name="위치"
                    ),
                ),
            ],
            options={
                "verbose_name": "이벤트",
                "verbose_name_plural": "이벤트",
                "ordering": ["start_time"],
            },
        ),
    ]
