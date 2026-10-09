import django.utils.timezone
import uuid
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0006_walk_finish"),
    ]

    operations = [
        migrations.CreateModel(
            name="ReminderSettings",
            fields=[
                ("id", models.UUIDField(default=uuid.uuid4, primary_key=True, serialize=False)),
                ("user_id", models.CharField(max_length=100, unique=True)),
                ("enabled", models.BooleanField(default=False)),
                ("weekday_time", models.CharField(default="18:00", max_length=5)),
                ("weekend_time", models.CharField(default="11:00", max_length=5)),
                ("timezone", models.CharField(default="Europe/Madrid", max_length=64)),
                ("language", models.CharField(choices=[("es", "Es"), ("en", "En")], default="es", max_length=5)),
                ("telegram_chat_id", models.CharField(blank=True, default="", max_length=30)),
                ("link_code", models.CharField(blank=True, db_index=True, default="", max_length=40)),
                ("last_sent_on", models.DateField(blank=True, null=True)),
                ("updated_at", models.DateTimeField(default=django.utils.timezone.now)),
            ],
        ),
    ]
