from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users.views import (
    PaymentCreateAPIView,
    PaymentListAPIView,
    PaymentRetrieveAPIView,
    PaymentUpdateAPIView,
    PaymentDeleteAPIView,
    PaymentViewSet
)

app_name = "users"

# Создаем роутер для ViewSet
router = DefaultRouter()
router.register(r'payments', PaymentViewSet)

urlpatterns = [
    # Отдельные URL для конкретных APIView
    path('payment/create/', PaymentCreateAPIView.as_view(), name='payment-create'),
    path('payment/', PaymentListAPIView.as_view(), name='payment-list'),
    path('payment/<int:pk>/', PaymentRetrieveAPIView.as_view(), name='payment'),
    path('payment/update/<int:pk>/', PaymentUpdateAPIView.as_view(), name='payment-update'),
    path('payment/delete/<int:pk>/', PaymentDeleteAPIView.as_view(), name='payment-delete'),

    # Добавляем URL от роутера
    path('', include(router.urls)),
]
