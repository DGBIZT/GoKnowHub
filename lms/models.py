from django.db import models
from users.models import CustomUser
from django.conf import settings


class Course(models.Model):
    title = models.CharField(
        max_length=255,
        verbose_name='Название',
        help_text='Введите название курса'
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
