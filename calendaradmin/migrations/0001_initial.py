from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="CalendarAdmin",
            fields=[
                ("admin_id", models.BigIntegerField(primary_key=True, serialize=False)),
            ],
        ),
    ]
