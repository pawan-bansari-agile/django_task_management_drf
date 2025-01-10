from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db import connections


class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from users.models import CustomUser  # Import here to avoid circular imports
        try:
            if 'users_customuser' in connections['default'].introspection.table_names():
                if not CustomUser.objects.filter(username='admin').exists():
                    CustomUser.objects.create_superuser(
                        username='admin',
                        email='super_admin@yopmail.com',
                        password='Admin@123',
                        role='admin',
                        first_name='Admin',
                        last_name='User'
                    )
        except OperationalError:
            # Skip if the database isn't ready yet
            pass