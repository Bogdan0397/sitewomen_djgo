from django.apps import AppConfig
import atexit

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'

    def ready(self):
        from . import cleanup_function
        atexit.register(cleanup_function.cleanup)

