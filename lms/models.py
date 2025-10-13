from django.db import models
from django.conf import settings
from django.utils import timezone
from djstripe.models import Product, Price
from django.db.models import OneToOneField


class Course(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Введите название курса'
    )

    price_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Стоимость курса',
        default = 0.00 # Значение по умолчанию
    )

    preview = models.ImageField(
        upload_to='courses/previews/',
        verbose_name='Превью',
        help_text='Загрузите изображение для превью курса',
        null=True,
        blank=True
    )

    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите подробное описание курса',
        blank=True
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь",)

    class Meta:
        verbose_name = 'Курс'
        verbose_name_plural = 'Курсы'
        ordering = ('-id',)

    def __str__(self):
        return self.title

    def get_preview_url(self):
        if self.preview:
            return self.preview.url
        return None

    def get_lessons_count(self):
        return self.lessons.count()


    def mark_as_purchased(self, user):
        # Логика отметки курса как купленного
        Subscription.objects.create(
            user=user,
            course=self,
            is_active=True
        )


class Lesson(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Введите название урока'
    )

    description = models.TextField(
        verbose_name='Описание',
        help_text='Введите подробное описание урока',
        blank=True
    )

    preview = models.ImageField(
        upload_to='lessons/previews/',
        verbose_name='Превью',
        help_text='Загрузите изображение для превью урока',
        null=True,
        blank=True
    )

    video_url = models.URLField(
        verbose_name='Ссылка на видео',
        help_text='Вставьте ссылку на видеоурок',
        blank=True
    )

    # Связь с курсом
    course = models.ForeignKey(
        Course,
        related_name='lessons',
        on_delete=models.CASCADE,
        verbose_name='Курс'
    )

    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        verbose_name="Пользователь", )

    class Meta:
        verbose_name = 'Урок'
        verbose_name_plural = 'Уроки'
        ordering = ("-id",)

    def __str__(self):
        return f"{self.title} | {self.course.title}"

    def get_preview_url(self):
        if self.preview:
            return self.preview.url
        return None

class Subscription(models.Model):
    """ Модель подписки на обновления курса для пользователя  """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='subscriptions',
        verbose_name='Пользователь'
    )

    course = models.ForeignKey(
        Course,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name='Курс'
    )

    # Добавляем дату создания подписки
    subscription_date = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата подписки'
    )

    # Добавляем статус активности подписки
    is_active = models.BooleanField(
        default=True,
        verbose_name='Активна'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        unique_together = ('user', 'course')  # Уникальное сочетание пользователя и курса
        ordering = ['-subscription_date']

    def __str__(self):
        return f"Подписка {self.user.email} на {self.course.title}"

    def activate(self):
        """Активировать подписку"""
        self.is_active = True
        self.save()

    def deactivate(self):
        """Деактивировать подписку"""
        self.is_active = False
        self.save()

    # def clean(self):
        # Валидация: проверка на подписку на собственный курс
        # if self.course.owner == self.user:
        #     raise ValidationError("Нельзя подписаться на собственный курс")