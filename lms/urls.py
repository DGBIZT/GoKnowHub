
from lms.apps import LmsConfig
from rest_framework.routers import DefaultRouter
from lms.views import (
    CourseViewSet,
    LessonCreateAPIView,
    LessonListAPIView,
    LessonRetrieveAPIView,
    LessonUpdateAPIView,
    LessonDeleteAPIView,
    SubscriptionView,
    CreateCheckoutSessionView,
    PaymentSuccessView,
    PaymentCancelView, CreateStripeCustomerView,
)
from django.urls import path


app_name = LmsConfig.name

router = DefaultRouter()
router.register(r"courses", CourseViewSet, basename="courses")

urlpatterns = [
        # Уроки
        path("lesson/create/", LessonCreateAPIView.as_view(), name="lesson-create"),
        path("lesson/", LessonListAPIView.as_view(), name="lesson-list"),
        path("lesson/<int:pk>/", LessonRetrieveAPIView.as_view(), name="lesson-detail"),
        path("lesson/update/<int:pk>/", LessonUpdateAPIView.as_view(), name="lesson-update"),
        path("lesson/delete/<int:pk>/", LessonDeleteAPIView.as_view(), name="lesson-delete"),

        # Подписки
        path('subscription/', SubscriptionView.as_view(), name='subscription'),

        # Платежи
        path('courses/<int:course_id>/checkout/', CreateCheckoutSessionView.as_view(),
                       name='create_checkout_session'),
        path('payment/success/', PaymentSuccessView.as_view(), name='payment_success'),
        path('payment/cancel/', PaymentCancelView.as_view(), name='payment_cancel'),
        path('stripe/customer/', CreateStripeCustomerView.as_view(), name='create_stripe_customer'),

] + router.urls
