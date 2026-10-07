from django.core.management.base import BaseCommand

from users.models import ensure_demo_hr_data


class Command(BaseCommand):
    help = 'Create the demo HR evaluation scenario used by the app.'

    def handle(self, *args, **options):
        result = ensure_demo_hr_data()
        self.stdout.write(self.style.SUCCESS(f"Demo HR data seeded: {result['team'].name}, manager={result['manager'].username}"))
