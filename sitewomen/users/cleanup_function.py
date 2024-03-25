from .models import User

def cleanup():
    # Удаление данных из базы данных при закрытии сервера
    User.objects.all().delete()