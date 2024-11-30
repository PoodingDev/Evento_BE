from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Calendar",
            fields=[
                (
                    "calendar_id",
                    models.BigIntegerField(primary_key=True, serialize=False),
                ),
                ("name", models.CharField(max_length=255)),
                ("description", models.TextField(blank=True, null=True)),
                ("is_public", models.BooleanField(default=False)),
                ("color", models.CharField(blank=True, max_length=20, null=True)),
                (
                    "invitation_code",
                    models.CharField(blank=True, max_length=255, null=True),
                ),
            ],
        ),
    ]
