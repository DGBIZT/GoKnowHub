from rest_framework.pagination import PageNumberPagination

class StandardResultsSetPagination(PageNumberPagination):
    # Количество элементов на странице по умолчанию
    page_size = 10
    # Параметр для указания размера страницы в запросе
    page_size_query_param = 'page_size'
    # Максимальный размер страницы
    max_page_size = 100

class CourseResultsSetPagination(PageNumberPagination):
    # Для курсов можно использовать больший размер страницы
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 100

class LessonResultsSetPagination(PageNumberPagination):
    # Для уроков можно использовать меньший размер страницы
    page_size = 2
    page_size_query_param = 'page_size'
    max_page_size = 50