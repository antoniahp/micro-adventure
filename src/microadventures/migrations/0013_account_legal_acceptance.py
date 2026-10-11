from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("microadventures", "0012_account_nickname_and_google"),
    ]

    operations = [
        migrations.AddField(
            model_name="account",
            name="legal_version",
            field=models.CharField(blank=True, max_length=20, null=True),
        ),
        migrations.AddField(
            model_name="account",
            name="legal_accepted_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]
