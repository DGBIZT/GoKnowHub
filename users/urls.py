from django.urls import path, include
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.routers import DefaultRouter
from users.views import (
    PaymentCreateAPIView,
    PaymentListAPIView,
    PaymentRetrieveAPIView,
    PaymentUpdateAPIView,
    PaymentDeleteAPIView,
    PaymentViewSet,
    UserDestroyAPIView,
    UserUpdateAPIView,
    UserCreateAPIView,
    UserRetrieveAPIView,
)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from users.apps import UsersConfig
from django.contrib import admin
from users.views import UserCreateAPIView
from rest_framework.permissions import AllowAny


app_name = UsersConfig.name

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

    path("register/", UserCreateAPIView.as_view(), name="register"),
    path('login/', TokenObtainPairView.as_view(permission_classes=(AllowAny,)), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(permission_classes=(AllowAny,)), name='token_refresh'),

    path('user/me/', UserRetrieveAPIView.as_view(), name='user-detail'),
    path('user/<int:pk>/', UserRetrieveAPIView.as_view(), name='user-detail'),# Получение информации о себе
    path('user/update/<int:pk>/', UserUpdateAPIView.as_view(), name='user-update'),  # Обновление информации
    path('user/delete/<int:pk>/', UserDestroyAPIView.as_view(), name='user-delete'),  # Удаление аккаунта

    # Добавляем URL от роутера
    path('', include(router.urls)),
]
