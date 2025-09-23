from django.contrib.auth.models import AbstractUser
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models


class CustomUser(AbstractUser):
    email = models.EmailField(unique=True, verbose_name='email address')
    phone_number = models.CharField(max_length=15, blank=True, null=True, verbose_name="Номер телефона")
    city = models.CharField(max_length=100, blank=True, verbose_name='Город')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name='Аватар')
    is_confirmed = models.BooleanField(default=False)
    is_blocked = models.BooleanField(default=False)




    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

class Payments(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name="пользователь")
    payment_data = models.DateField(verbose_name="дата оплаты")
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма оплаты") # Сумма оплаты. decimal_places=2 означает сохранение и отображение числа с двумя знаками после запятой.
    payment_method = models.CharField(max_length=20, choices=[('cash', 'Наличные'), ('transfer', 'Перевод')], verbose_name="метод оплаты")

    # Generic Foreign Key поля
    # content_type хранит информацию о типе объекта (модель)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE
    )
    # object_id — хранит ID конкретного объекта
    object_id = models.PositiveIntegerField()
    # content_object — виртуальное поле, которое объединяет предыдущие два и позволяет получить реальный объект
    content_object = GenericForeignKey('content_type', 'object_id')


    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

    def __str__(self):
        return f"{self.user} - {self.payment_data} - {self.amount} - {self.payment_method}"