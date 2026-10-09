from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0005_challenge_source"),
    ]

    operations = [
        migrations.AddField(
            model_name="walk",
            name="walked_minutes",
            field=models.PositiveSmallIntegerField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="walk",
            name="distance_km",
            field=models.FloatField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="walk",
            name="diary",
            field=models.CharField(blank=True, default="", max_length=2000),
        ),
        migrations.AddField(
            model_name="walk",
            name="finished_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
