from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.exceptions import ValidationError
from users.models import Payments
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

# Получение модели пользователя
User = get_user_model()

class Command(BaseCommand):
    help = 'Заполнение таблицы модели Payments через командную строку. Пример: python manage.py add_payments.'

    def handle(self, *args, **options):

        try:
            # Пытаемся найти пользователя testadmin@sky.pro
            target_user = User.objects.get(username='admin')
        except User.DoesNotExist:
            try:
                # Если не нашли по username, пробуем найти по email
                target_user = User.objects.get(email='testadmin@sky.pro')
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR("Пользователь testadmin@sky.pro не найден в системе!")
                )
                return

        payments_data = [
            {"user": target_user, "payment_data": "2025-09-23", "amount": 5000.00, "payment_method": "cash", "content_type": 1, "object_id": 1,},
            {"user": target_user, "payment_data": "2025-09-23", "amount": 1000.00, "payment_method": 'transfer', "content_type": 1,"object_id": 3, },

        ]

        created_count = 0
        skipped_count = 0

        for data in payments_data:
            try:
                # Преобразуем строку даты в объект даты
                payment_date = timezone.datetime.strptime(data['payment_data'], '%Y-%m-%d').date()

                # Получаем content_type объект
                content_type = ContentType.objects.get_for_id(data['content_type'])

                payment, created = Payments.objects.get_or_create(
                    user=data['user'],
                    payment_data=payment_date,
                    amount=data['amount'],
                    payment_method=data['payment_method'],
                    content_type=content_type,
                    object_id=data['object_id'],
                )

                if created:
                    created_count += 1
                    self.stdout.write(
                        self.style.SUCCESS(f"Успешно создано платежное поручение: {payment.id}")
                    )
                else:
                    skipped_count += 1
                    self.stdout.write(
                        self.style.WARNING(f"Платежное поручение уже существует: {payment.id}")
                    )

            except ValidationError as ve:
                self.stdout.write(
                    self.style.ERROR(f"Ошибка валидации при создании платежа: {ve}")
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f"Произошла ошибка при создании платежа: {str(e)}")
                )

        self.stdout.write(
            self.style.SUCCESS(
                f"Операция завершена. Создано: {created_count}, пропущено: {skipped_count}"
            )
        )