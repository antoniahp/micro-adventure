from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0004_walk_language"),
    ]

    operations = [
        migrations.AddField(
            model_name="challenge",
            name="source",
            field=models.CharField(default="template", max_length=60),
        ),
    ]
