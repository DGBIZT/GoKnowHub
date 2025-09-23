from rest_framework import serializers

from lms.models import Course, Lesson


class CourseSerializer(serializers.ModelSerializer):

    number_of_lessons = serializers.SerializerMethodField()

    class Meta:
        model = Course
        fields = '__all__'

    def get_number_of_lessons(self, instance):
        # Подсчет количества уроков через related_name который находится в модели Lesson
        # instance.lessons — получаем queryset всех уроков курса
        # .count() — считаем количество записей в queryset
        try:
            return instance.lessons.count()
        except Exception as e:
            print(f"Ошибка подсчета уроков: {e}")
            return 0


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'