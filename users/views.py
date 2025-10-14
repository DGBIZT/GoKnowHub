import stripe
from django.http import Http404
from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend
from requests import session
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from config import settings
from users.models import Payments
from users.permissions import IsOwner
from users.serializers import PaymentSerializer, UserSerializer
from rest_framework import viewsets
from users.models import CustomUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response

from users.services import create_stripe_product, create_stripe_price, create_stripe_checkout_session
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer

    @swagger_auto_schema(
        request_body=PaymentSerializer,
        responses={
            201: "Платеж успешно создан",
            400: "Неверные данные платежа",
            500: "Ошибка при обработке платежа"
        },
        operation_description="Создание нового платежа"
    )
    def create(self, request, *args, **kwargs):
        # Проверка на аутентификацию
        if not request.user.is_authenticated:
            return Response(
                {'detail': 'Пользователь не аутентифицирован'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        try:
            # Получаем курс из валидированных данных
            course = serializer.validated_data['course']

            # Инициализация Stripe
            stripe.api_key = settings.STRIPE_SECRET_KEY

            # Создаем продукт и цену в Stripe
            product_id = create_stripe_product(
                course.title,
                course.description
            )
            price_id = create_stripe_price(
                product_id,
                int(course.price * 100)
            )

            # Формируем URL успеха
            success_url = f"http://127.0.0.1:8000/courses/{course.id}/"

            # Создаем сессию Stripe
            session = create_stripe_checkout_session(
                price_id=price_id,
                success_url=success_url
            )

            # Сохраняем все данные за один раз
            serializer.save(
                user=self.request.user,
                course=course,
                amount=course.price,
                payment_method=serializer.validated_data['payment_method'],
                stripe_id=session.id,
                payment_url=session.url
            )

        except stripe.StripeError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            return Response(
                {'error': 'Произошла ошибка при обработке платежа'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("payment_method",)
    ordering_fields = ("payment_data",)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()

        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                name='payment_method',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Фильтр по методу оплаты'
            ),
            openapi.Parameter(
                name='ordering',
                in_=openapi.IN_QUERY,
                type=openapi.TYPE_STRING,
                description='Сортировка по дате'
            )
        ],
        responses={200: PaymentSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: PaymentSerializer},
        operation_description="Получение информации о платеже"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()
        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)

class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=PaymentSerializer,
        responses={
            200: "Платеж успешно обновлен",
            400: "Неверные данные",
            403: "Нет прав доступа"
        },
        operation_description="Обновление информации о платеже"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()
        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)



class PaymentDeleteAPIView(generics.DestroyAPIView):
    queryset = Payments.objects.all()
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(  # Убрали method='delete'
        responses={
            204: "Платеж успешно удален",
            403: "Нет прав доступа",
            404: "Платеж не найден"
        },
        operation_description="Удаление платежа"
    )
    def destroy(self, request, *args, **kwargs):
        # Добавляем проверку прав доступа
        instance = self.get_object()
        if not request.user.is_superuser and instance.user != request.user:
            return Response({'detail': 'У вас нет прав на удаление этого платежа'}, status=status.HTTP_403_FORBIDDEN)

        return super().destroy(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()
        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]
    queryset = Payments.objects.all()

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()
        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)


    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=PaymentSerializer,
        responses={
            200: "Платеж успешно обновлен",
            400: "Неверные данные",
            403: "Нет прав доступа"
        },
        operation_description="Обновление информации о платеже"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        responses={
            204: openapi.Response(description="Платеж успешно удален"),
            403: openapi.Response(description="Нет прав доступа"),
            404: openapi.Response(description="Платеж не найден")
        },
        operation_description="Удаление платежа"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            201: openapi.Response(description="Пользователь успешно создан",
                                  content={'application/json': UserSerializer}),
            400: openapi.Response(description="Неверные данные")
        }
    )
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)
    queryset = CustomUser.objects.all()

    @swagger_auto_schema(
        responses={
            200: openapi.Response(description="Информация о пользователе",
                                  content={'application/json': UserSerializer}),
            404: openapi.Response(description="Пользователь не найден"),
            403: openapi.Response(description="Нет прав доступа")
        },
        operation_description="Получение информации о пользователе"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()
        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={
            200: openapi.Response(description="Пользователь успешно обновлен",
                                  content={'application/json': UserSerializer}),
            400: openapi.Response(description="Неверные данные"),
            403: openapi.Response(description="Нет прав доступа")
        },
        operation_description="Обновление информации о пользователе"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    def get_object(self):
        # Проверяем, является ли пользователь суперпользователем
        if self.request.user.is_superuser:
            try:
                return CustomUser.objects.get(pk=self.kwargs['pk'])
            except CustomUser.DoesNotExist:
                raise Http404("Пользователь не найден")
        # Для обычных пользователей возвращаем только их профиль
        return self.request.user

    def get_queryset(self):
        user = self.request.user
        if not user.is_authenticated:
            return Payments.objects.none()
        if user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=user)


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # Пользователь может удалять только свою учетную запись
        if self.request.user.is_superuser:
            return CustomUser.objects.get(pk=self.kwargs['pk'])
        return self.request.user

    class UserDestroyAPIView(generics.DestroyAPIView):
        queryset = CustomUser.objects.all()
        permission_classes = (IsAuthenticated,)

    @swagger_auto_schema(
        responses={
            204: openapi.Response(description="Пользователь успешно удален"),
            403: openapi.Response(description="Нет прав доступа"),
            404: openapi.Response(description="Пользователь не найден")
        },
        operation_description="Удаление учетной записи пользователя"
    )
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user and not request.user.is_superuser:
            raise PermissionDenied("У вас нет прав на удаление этого пользователя")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)