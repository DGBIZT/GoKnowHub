
from lms.apps import LmsConfig
from rest_framework.routers import DefaultRouter
from lms.views import CourseViewSet, LessonCreateAPIView, LessonListAPIView,LessonRetrieveAPIView, LessonUpdateAPIView, LessonDeleteAPIView, SubscriptionView, CreateCheckoutSessionView
from django.urls import path

app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")


urlpatterns = [
    path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
    path("lesson/", LessonListAPIView.as_view(), name="lesson-list"),
    path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson"),
    path("lesson/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"),
    path("lesson/delete/<int:pk>/", LessonDeleteAPIView.as_view(), name="lesson-delete"),
    path('subscription/', SubscriptionView.as_view(), name='subscription'),
    path('courses/<int:course_id>/checkout/', CreateCheckoutSessionView.as_view(), name='create_checkout_session'),

] + router.urls
