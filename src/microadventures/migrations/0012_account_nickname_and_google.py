from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0011_account"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="nickname",
            field=models.CharField(blank=True, max_length=50, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="google_sub",
            field=models.CharField(blank=True, db_index=True, max_length=255, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="google_email_hash",
            field=models.CharField(blank=True, max_length=64, null=True),
        ),
    ]
