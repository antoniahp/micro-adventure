from django.core.management.base import BaseCommand

from microadventures.domain.models.account import Account
from microadventures.domain.models.reminder_settings import ReminderSettings
from microadventures.domain.models.support_code import normalize, support_code
from microadventures.domain.models.walk import Walk
from microadventures.domain.models.weekly_reflection import WeeklyReflection


class Command(BaseCommand):
    help = "Finds the account behind the code a person sent by email (the one shown in Settings → Your data)."

    def add_arguments(self, parser):
        parser.add_argument("code", help='For example "MA-7K3F-9Q2X" (case and dashes don\'t matter)')

    def handle(self, *args, code: str, **options):
        wanted = normalize(code)
        # The code can't be reversed, so every account is checked: fine for a few thousand of them.
        matches = [a.user_id for a in Account.objects.only("user_id") if support_code(a.user_id) == wanted]
        if not matches:
            self.stdout.write(f"No account has the code {wanted}.")
            return
        for user_id in matches:
            self.stdout.write(
                f"{wanted} → user_id {user_id}: "
                f"{Walk.objects.filter(user_id=user_id).count()} walks, "
                f"{WeeklyReflection.objects.filter(user_id=user_id).count()} reflections, "
                f"reminders {'yes' if ReminderSettings.objects.filter(user_id=user_id).exists() else 'no'}"
            )
