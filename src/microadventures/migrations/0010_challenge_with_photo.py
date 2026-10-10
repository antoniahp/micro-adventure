from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0009_weather_and_card"),
    ]

    operations = [
        migrations.AddField(
            model_name="challenge",
            name="with_photo",
            field=models.BooleanField(default=False),
        ),
    ]
