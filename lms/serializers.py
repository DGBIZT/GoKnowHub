from rest_framework import serializers

from lms.models import Course, Lesson
from lms.validators import LinkYouTubeValidator
from lms.models import Subscription



class LessonSerializer(serializers.ModelSerializer):


    class Meta:
        model = Lesson
        fields = '__all__'
        validators = [
            LinkYouTubeValidator('video_url')  # Добавляем валидатор здесь
        ]



class CourseSerializer(serializers.ModelSerializer):

    number_of_lessons = serializers.SerializerMethodField()
    lesson_info = LessonSerializer( source="lessons", many=True, read_only=True)
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = ["id", "title", "number_of_lessons", 'price_amount',"lesson_info", "preview", "description", 'owner', 'is_subscribed']

    def get_number_of_lessons(self, instance):
        # Подсчет количества уроков через related_name который находится в модели Lesson
        # instance.lessons — получаем queryset всех уроков курса
        # .count() — считаем количество записей в queryset
        try:
            return instance.lessons.count()
        except Exception as e:
            print(f"Ошибка подсчета уроков: {e}")
            return 0

    def get_is_subscribed(self, obj):
        # Получаем текущего пользователя из контекста
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            # Проверяем наличие подписки
            return Subscription.objects.filter(
                user=request.user,
                course=obj
            ).exists()
        return False
