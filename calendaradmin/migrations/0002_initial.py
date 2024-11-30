import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("calendaradmin", "0001_initial"),
        ("calendars", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="calendaradmin",
            name="calendar_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="calendars.calendar"
            ),
        ),
    ]
