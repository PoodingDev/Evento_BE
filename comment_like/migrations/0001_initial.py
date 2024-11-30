import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ("comment", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="CommentLike",
            fields=[
                ("like_id", models.BigAutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "comment_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="comment.comment",
                    ),
                ),
            ],
        ),
    ]
