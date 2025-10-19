from celery import shared_task
from django.core.mail import send_mail
from django.core.exceptions import ObjectDoesNotExist
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
import logging

from lms.models import Subscription, Course

# Настраиваем логирование
logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3, default_retry_delay=60)
def send_course_update_email(self, course_id):
    try:
        # Проверяем существование курса
        try:
            course = Course.objects.get(id=course_id)
        except Course.DoesNotExist:
            logger.warning(f"Курс с ID {course_id} не найден")
            return

        # Получаем подписчиков
        subscriptions = Subscription.objects.filter(course=course)
        if not subscriptions.exists():
            logger.info(f"Нет подписчиков для курса {course.id}")
            return

        # Формируем email список
        emails = [sub.user.email for sub in subscriptions]
        if not emails:
            logger.info(f"Нет валидных email для курса {course.id}")
            return

        # Формируем письмо
        subject = f'Обновление курса: {course.title}'
        html_message = render_to_string(
            'emails/course_update.html',
            {'course': course}
        )
        plain_message = strip_tags(html_message)

        # Отправляем
        send_mail(
            subject,
            plain_message,
            settings.DEFAULT_FROM_EMAIL,
            emails,
            html_message=html_message,
            fail_silently=False
        )

        logger.info(f"Успешно отправлены уведомления для курса {course.id}")

    except Exception as e:
        logger.error(f"Ошибка при отправке уведомлений для курса {course_id}: {str(e)}")
        self.retry(exc=e)
