from rest_framework import serializers

from lms.models import Course, Lesson


class LessonSerializer(serializers.ModelSerializer):

    class Meta:
        model = Lesson
        fields = '__all__'



class CourseSerializer(serializers.ModelSerializer):

    number_of_lessons = serializers.SerializerMethodField()
    lesson_info = LessonSerializer( source="lessons", many=True, read_only=True)

    class Meta:
        model = Course
        fields = ["id", "title", "number_of_lessons", "lesson_info", "preview", "description", 'owner']

    def get_number_of_lessons(self, instance):
        # Подсчет количества уроков через related_name который находится в модели Lesson
        # instance.lessons — получаем queryset всех уроков курса
        # .count() — считаем количество записей в queryset
        try:
            return instance.lessons.count()
        except Exception as e:
            print(f"Ошибка подсчета уроков: {e}")
            return 0
