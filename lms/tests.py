from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from django.contrib.auth.models import Group
from users.models import CustomUser
from lms.models import Course, Lesson, Subscription
from django.utils import timezone

class LessonCRUDAndSubscriptionTest(APITestCase):
    def setUp(self):
        # Создаем тестовых пользователей
        self.user1 = CustomUser.objects.create_user(
            email='user1@test.com',
            password='123456',
            username='user1'
        )

        self.user2 = CustomUser.objects.create_user(
            email='user2@test.com',
            password='123456',
            username='user2'
        )

        # Создаем группу модераторов
        moderators_group = Group.objects.create(name='moderators')
        self.moderator = CustomUser.objects.create_user(
            email='moderator@test.com',
            password='123456',
            username='moderator'
        )
        moderators_group.user_set.add(self.moderator)

        # Создаем тестовые курсы
        self.course1 = Course.objects.create(
            title='Курс 1',
            owner=self.user1
        )

        self.course2 = Course.objects.create(
            title='Курс 2',
            owner=self.user2
        )

        # Создаем тестовый урок
        self.lesson = Lesson.objects.create(
            title='Урок 1',
            description='Описание урока',
            course=self.course1,
            owner=self.user1
        )

    # Тесты CRUD для уроков
    def test_list_lessons(self):
        response = self.client.get(reverse('lms:lesson-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_create_lesson(self):
        self.client.force_authenticate(user=self.user1)

        data = {
            'title': 'Новый урок',
            'description': 'Новое описание',
            'course': self.course1.id,
            'video_url': 'https://www.youtube.com/watch?v=123'
        }

        response = self.client.post(reverse('lms:lesson-create'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Lesson.objects.count(), 2)

    def test_update_lesson(self):
        self.client.force_authenticate(user=self.user1)

        # Получаем существующий урок для обновления
        url = reverse('lms:lesson-update', kwargs={'pk': self.lesson.id})

        # Формируем полные данные для обновления, включая все обязательные поля
        data = {
            'title': 'Обновленный урок',
            'description': 'Обновленное описание',
            'course': self.lesson.course.id,  # Добавляем course
            'video_url': self.lesson.video_url,  # Добавляем video_url
            'owner': self.lesson.owner.id  # Добавляем owner, если он не readonly
        }

        response = self.client.put(url, data, format='json')

        # Добавляем отладку для просмотра ошибок
        print("Статус ответа:", response.status_code)
        print("Содержимое ответа:", response.content)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Lesson.objects.get(id=self.lesson.id).title, 'Обновленный урок')

    def test_delete_lesson(self):
        self.client.force_authenticate(user=self.user1)

        # Используем правильное имя URL
        url = reverse('lms:lesson-delete', kwargs={'pk': self.lesson.id})
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Lesson.objects.count(), 0)

    def test_subscribe_to_course(self):
        """ Тесты для подписки на курсы """
        self.client.force_authenticate(user=self.user2)

        data = {
            'course_id': self.course1.id  # Изменили ключ на 'course_id'
        }

        response = self.client.post(reverse('lms:subscription'), data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 1)
        self.assertTrue(self.course1.subscribers.filter(user=self.user2).exists())

    def test_duplicate_subscription(self):
        # Первая подписка
        self.client.force_authenticate(user=self.user2)

        # Используем правильное имя URL
        self.client.post(
            reverse('lms:subscription'),  # Изменили имя URL
            {'course_id': self.course1.id},  # Используем course_id вместо course
            format='json'
        )

        # Повторная попытка подписки
        response = self.client.post(
            reverse('lms:subscription'),  # Используем правильное имя URL
            {'course_id': self.course1.id},  # Используем course_id
            format='json'
        )

        # Проверяем, что возвращается 200 OK, так как подписка удаляется при повторном запросе
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Subscription.objects.count(), 0)  # Подписка должна быть удалена
        self.assertEqual(
            response.data['message'],
            'Подписка удалена'  # Проверяем сообщение в ответе
        )

    def tearDown(self):
        # Очистка после тестов
        CustomUser.objects.all().delete()
        Course.objects.all().delete()
        Lesson.objects.all().delete()
        Subscription.objects.all().delete()
        Group.objects.all().delete()
