# users/tasks.py
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from users.models import CustomUser


@shared_task
def block_inactive_users():
    # Получаем текущую дату
    now = timezone.now()

    # Рассчитываем дату месяц назад
    one_month_ago = now - timedelta(days=30)

    # Находим всех пользователей, которые не заходили более месяца
    inactive_users = CustomUser.objects.filter(
        last_login__lt=one_month_ago,
        is_active=True
    )

    # Блокируем найденных пользователей
    for user in inactive_users:
        user.is_active = False
        user.save()
        print(f"Заблокирован пользователь: {user.email}")
