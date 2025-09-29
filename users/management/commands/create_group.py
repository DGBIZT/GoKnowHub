from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group
from django.contrib.auth import get_user_model

User = get_user_model()  # Получаем вашу кастомную модель пользователя

class Command(BaseCommand):
    """
        Создание новой группы - python manage.py create_group "moderators"
        Создание группы с пользователями (добавление по email) - python manage.py create_group "Модераторы" --users user1@example.com user2@example.com
        Удаление группы - python manage.py create_group "moderators" --delete

    """
    help = 'Создание и управление группами пользователей'

    def add_arguments(self, parser):
        # Обязательный аргумент - название группы
        parser.add_argument(
            'group_name',
            type=str,
            help='Название создаваемой группы'
        )
        # Опциональный аргумент - список пользователей (по email)
        parser.add_argument(
            '--users',
            nargs='+',
            type=str,
            help='Список email пользователей для добавления в группу'
        )
        # Опциональный аргумент - флаг удаления группы
        parser.add_argument(
            '--delete',
            action='store_true',
            help='Удалить группу'
        )

    def handle(self, *args, **kwargs):
        group_name = kwargs['group_name']
        users = kwargs.get('users')
        delete = kwargs.get('delete')

        if delete:
            try:
                group = Group.objects.get(name=group_name)
                group.delete()
                self.stdout.write(self.style.SUCCESS(f'Группа {group_name} успешно удалена'))
            except Group.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'Группа {group_name} не найдена'))
            return

        # Создание или получение существующей группы
        group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа {group_name} успешно создана'))
        else:
            self.stdout.write(f'Группа {group_name} уже существует')

        # Добавление пользователей в группу по email
        if users:
            for user_email in users:
                try:
                    user = User.objects.get(email=user_email)
                    group.user_set.add(user)
                    self.stdout.write(self.style.SUCCESS(f'Пользователь {user_email} добавлен в группу {group_name}'))
                except User.DoesNotExist:
                    self.stdout.write(self.style.ERROR(f'Пользователь с email {user_email} не найден'))

