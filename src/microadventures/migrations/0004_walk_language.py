from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0003_challenge_story"),
    ]

    operations = [
        migrations.AddField(
            model_name="walk",
            name="language",
            field=models.CharField(choices=[("es", "Es"), ("en", "En")], default="es", max_length=5),
        ),
    ]
