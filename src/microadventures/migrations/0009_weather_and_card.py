from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0008_weeklyreflection"),
    ]

    operations = [
        migrations.AddField(model_name="walk", name="conditions", field=models.CharField(blank=True, default="", max_length=60)),
        migrations.AddField(model_name="remindersettings", name="latitude", field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name="remindersettings", name="longitude", field=models.FloatField(blank=True, null=True)),
        migrations.AddField(model_name="remindersettings", name="snoozed_until", field=models.DateTimeField(blank=True, null=True)),
    ]
