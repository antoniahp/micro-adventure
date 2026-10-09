import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0007_remindersettings"),
    ]

    operations = [
        migrations.CreateModel(
            name="WeeklyReflection",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("user_id", models.CharField(db_index=True, max_length=100)),
                ("week_start", models.DateField()),
                ("feeling", models.PositiveSmallIntegerField()),
                ("note", models.CharField(blank=True, default="", max_length=500)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
