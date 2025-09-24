import django_filters
from lms.models import Course

class CourseFilter(django_filters.FilterSet):
    """ Поиск по полю title в модели Course """
    title = django_filters.CharFilter(lookup_expr='icontains') # Поиск по части названия

    class Meta:
        model = Course
        fields = ['title']  # Добавляем поля для фильтрации