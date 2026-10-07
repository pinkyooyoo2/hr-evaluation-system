from django.core.management.base import BaseCommand

from users.models import User


class Command(BaseCommand):
    help = 'Create default admin user if it does not exist.'

    def handle(self, *args, **options):
        user, created = User.objects.get_or_create(
            username='ADMIN',
            defaults={
                'name': 'ADMIN',
                'role': 'admin',
                'is_staff': True,
                'is_superuser': True,
            },
        )

        if created:
            user.set_password('admin1234!')
            user.save()
            self.stdout.write(self.style.SUCCESS('Default admin user created.'))
            return

        user.name = 'ADMIN'
        user.role = 'admin'
        user.is_staff = True
        user.is_superuser = True
        user.set_password('admin1234!')
        user.save()
        self.stdout.write(self.style.SUCCESS('Default admin user already existed. Updated to required values.'))
