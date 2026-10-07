from django.apps import AppConfig
from django.db import connection


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        try:
            if connection.introspection.table_names():
                from users.models import ensure_default_admin, ensure_demo_hr_data
                ensure_default_admin()
                ensure_demo_hr_data()
        except Exception:
            pass
