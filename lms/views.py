from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated, AllowAny

from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .filters import CourseFilter
from users.permissions import IsModer, IsOwner, IsModerOrOwner
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404

from lms.paginators import CourseResultsSetPagination, LessonResultsSetPagination
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

class CourseViewSet(viewsets.ModelViewSet):

    serializer_class = CourseSerializer
    # queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend]  # Добавляем бэкенд фильтрации
    filterset_class = CourseFilter  # Указываем наш фильтр
    permission_classes = [IsAuthenticated, IsModerOrOwner]
    pagination_class = CourseResultsSetPagination

    def get_permissions(self):
        # Определяем разные разрешения для разных действий
        if self.action in ['list', 'retrieve']:
            # Для просмотра списка и получения одного курса не требуется аутентификация
            self.permission_classes = [AllowAny]
        else:
            # Для остальных действий (create, update, destroy) требуется аутентификация
            self.permission_classes = [IsAuthenticated, IsModerOrOwner]
        return super().get_permissions()

    def get_queryset(self):
        # Фильтрация по владельцу
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='moderators').exists():
                return Course.objects.all()
            return Course.objects.filter(owner=self.request.user)
        return Course.objects.all()  # Для неавторизованных пользователей показываем все курсы

    @swagger_auto_schema(
        operation_description="Создание нового курса",
        request_body=CourseSerializer,
        responses={
            201: "Курс успешно создан",
            400: "Неверные данные",
            403: "Нет прав доступа"
        }
    )
    def create(self, request, *args, **kwargs):
        # Проверяем, является ли данные списком
        if isinstance(request.data, list):
            # Массовое создание объектов
            serializer = self.get_serializer(data=request.data, many=True)
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            # Одиночное создание объекта
            return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение списка курсов",
        manual_parameters=[
            openapi.Parameter(
                name='search',
                in_="query",
                type="string",
                description="Поиск по названию курса"
            ),
            openapi.Parameter(
                name='owner',
                in_="query",
                type="integer",
                description="ID владельца курса"
            )
        ],
        responses={
            200: CourseSerializer(many=True),
            403: "Нет прав доступа"
        }
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Получение информации о курсе по ID",
        responses={
            200: CourseSerializer,
            404: "Курс не найден",
            403: "Нет прав доступа"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


    def perform_create(self, serializer):

        return serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="Удаление курса",
        responses={
            204: "Курс успешно удален",
            404: "Курс не найден",
            403: "Нет прав доступа"
        }
    )
    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='moderators').exists():
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'У модераторов нет прав на удаление'})
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

    @swagger_auto_schema(
        operation_description="Обновление курса",
        request_body=CourseSerializer,
        responses={
            200: "Курс успешно обновлен",
            400: "Неверные данные",
            404: "Курс не найден",
            403: "Нет прав доступа"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Частичное обновление курса",
        request_body=CourseSerializer,
        responses={
            200: "Курс успешно обновлен",
            400: "Неверные данные",
            404: "Курс не найден",
            403: "Нет прав доступа"
        }
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = (~IsModer, IsAuthenticated)


    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)

    @swagger_auto_schema(
        operation_description="Создание нового урока",
        request_body=LessonSerializer,
        responses={
            201: "Урок успешно создан",
            400: "Неверные данные",
            403: "Нет прав доступа"
        }
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)



class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    # queryset = Lesson.objects.all()
    filter_backends = [DjangoFilterBackend] # Добавляем бэкенд фильтрации
    filterset_fields = ('title', 'course') # Указываем наш фильтр
    permission_classes = [IsAuthenticated, IsModerOrOwner]
    pagination_class = LessonResultsSetPagination

    def get_permissions(self):
        # Проверяем текущий метод запроса
        if self.request.method == 'GET':
            # Для GET-запросов (получение списка) не требуется аутентификация
            return [AllowAny()]
        else:
            # Для остальных методов требуется аутентификация
            return [IsAuthenticated(), IsModerOrOwner()]

    def get_queryset(self):
        # Фильтрация по владельцу курса
        if self.request.user.is_authenticated:
            if self.request.user.groups.filter(name='moderators').exists():
                return Lesson.objects.all()
            return Lesson.objects.filter(course__owner=self.request.user)
        return Lesson.objects.all()  # Для неавторизованных пользователей показываем все уроки

    @swagger_auto_schema(
        operation_description="Получение списка курсов",
        manual_parameters=[
            openapi.Parameter(
                name='search',
                in_="query",
                type="string",
                description="Поиск по названию"
            ),
            openapi.Parameter(
                name='owner',
                in_="query",
                type="integer",
                description="ID владельца"
            )
        ],
        responses={
            200: LessonSerializer(many=True),
            403: "Нет прав доступа"
        }
    )
    def list(self, request, *args, **kwargs):
        # Переопределяем метод list для дополнительной логики
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

class LessonRetrieveAPIView(generics.RetrieveAPIView):

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerOrOwner]

    @swagger_auto_schema(
        operation_description="Получение информации об уроке",
        responses={
            200: LessonSerializer,
            404: "Урок не найден",
            403: "Нет прав доступа"
        }
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)


class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerOrOwner]

    @swagger_auto_schema(
        operation_description="Обновление урока",
        request_body=LessonSerializer,
        responses={
            200: "Урок успешно обновлен",
            400: "Неверные данные",
            404: "Урок не найден",
            403: "Нет прав доступа"
        }
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

class LessonDeleteAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerOrOwner]

    @swagger_auto_schema(
        operation_description="Удаление урока",
        responses={
            204: "Урок успешно удален",
            404: "Урок не найден",
            403: "Нет прав доступа"
        }
    )
    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='moderators').exists():
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'У модераторов нет прав на удаление'})
        return super().destroy(request, *args, **kwargs)

class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Подписка на курс",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'course_id': openapi.Schema(type=openapi.TYPE_INTEGER, description="ID курса")
            },
            required=['course_id']
        ),
        responses={
            200: "Успешная операция",
            400: "Неверные данные",
            404: "Курс не найден"
        }
    )
    def post(self, request, *args, **kwargs):

        user = request.user
        course_id = request.data.get('course_id')

        if not course_id:
            return Response({
                "error": "course_id is required"
            }, status=status.HTTP_400_BAD_REQUEST)

        course = get_object_or_404(Course, id=course_id)

        # Проверяем существующую подписку
        subscription = Subscription.objects.filter(
            user=user,
            course=course
        ).first()

        if subscription:
            # Если подписка существует - удаляем
            subscription.delete()
            message = "Подписка удалена"
        else:
            # Если подписки нет - создаем
            Subscription.objects.create(
                user=user,
                course=course
            )
            message = "Подписка добавлена"

        return Response({
            "message": message
        }, status=status.HTTP_200_OK)
