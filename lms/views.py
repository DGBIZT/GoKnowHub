from django.shortcuts import render
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import viewsets, status, generics
from rest_framework.permissions import IsAuthenticated

from lms.models import Course, Lesson, Subscription
from lms.serializers import CourseSerializer, LessonSerializer
from rest_framework.response import Response
from django_filters import rest_framework as filters
from .filters import CourseFilter
from users.permissions import IsModer, IsOwner, IsModerOrOwner
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404




class CourseViewSet(viewsets.ModelViewSet):
    serializer_class = CourseSerializer
    # queryset = Course.objects.all()
    filter_backends = [DjangoFilterBackend]  # Добавляем бэкенд фильтрации
    filterset_class = CourseFilter  # Указываем наш фильтр
    permission_classes = [IsAuthenticated, IsModerOrOwner]

    def get_queryset(self):
        # Фильтрация по владельцу
        if self.request.user.groups.filter(name='moderators').exists():
            return Course.objects.all()
        return Course.objects.filter(owner=self.request.user)

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

    def perform_create(self, serializer):

        return serializer.save(owner=self.request.user)

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='moderators').exists():
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'У модераторов нет прав на удаление'})
        return super().destroy(request, *args, **kwargs)

    def get_serializer_context(self):
        context = super().get_serializer_context()
        context.update({"request": self.request})
        return context

class LessonCreateAPIView(generics.CreateAPIView):
    serializer_class = LessonSerializer
    permission_classes = (~IsModer, IsAuthenticated)

    def perform_create(self, serializer):
        return serializer.save(owner=self.request.user)


class LessonListAPIView(generics.ListAPIView):
    serializer_class = LessonSerializer
    # queryset = Lesson.objects.all()
    filter_backends = [DjangoFilterBackend] # Добавляем бэкенд фильтрации
    filterset_fields = ('title', 'course') # Указываем наш фильтр
    permission_classes = [IsAuthenticated, IsModerOrOwner]

    def get_queryset(self):
        # Фильтрация по владельцу курса
        if self.request.user.groups.filter(name='moderators').exists():
            return Lesson.objects.all()
        return Lesson.objects.filter(course__owner=self.request.user)

class LessonRetrieveAPIView(generics.RetrieveAPIView):

    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerOrOwner]

class LessonUpdateAPIView(generics.UpdateAPIView):
    serializer_class = LessonSerializer
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerOrOwner]

class LessonDeleteAPIView(generics.DestroyAPIView):
    queryset = Lesson.objects.all()
    permission_classes = [IsAuthenticated, IsModerOrOwner]

    def destroy(self, request, *args, **kwargs):
        if request.user.groups.filter(name='moderators').exists():
            return Response(status=status.HTTP_403_FORBIDDEN, data={'detail': 'У модераторов нет прав на удаление'})
        return super().destroy(request, *args, **kwargs)

class SubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

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