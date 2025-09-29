from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics, status
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny, IsAuthenticated

from users.models import Payments
from users.permissions import IsOwner
from users.serializers import PaymentSerializer, UserSerializer
from rest_framework import viewsets
from users.models import CustomUser
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response



class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer

    def perform_create(self, serializer):
        serializer.save(user=self.request.user) # Автоматически привязываем к текущему пользователю

class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("payment_method",)
    ordering_fields = ("payment_data",)

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=self.request.user)


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=self.request.user)

class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=self.request.user)

class PaymentDeleteAPIView(generics.DestroyAPIView):
    queryset = Payments.objects.all()

    def get_queryset(self):
        if self.request.user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=self.request.user)

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'object_id']
    permission_classes = [IsOwner]

    def get_queryset(self):
        # Фильтрация по пользователю
        if self.request.user.is_superuser:
            return Payments.objects.all()
        return Payments.objects.filter(user=self.request.user)

class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)


class UserRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # Пользователь может получать только свою информацию
        if self.request.user.is_superuser:
            return CustomUser.objects.get(pk=self.kwargs['pk'])
        return self.request.user


class UserUpdateAPIView(generics.UpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # Пользователь может обновлять только свою информацию
        if self.request.user.is_superuser:
            return CustomUser.objects.get(pk=self.kwargs['pk'])
        return self.request.user


class UserDestroyAPIView(generics.DestroyAPIView):
    queryset = CustomUser.objects.all()
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        # Пользователь может удалять только свою учетную запись
        if self.request.user.is_superuser:
            return CustomUser.objects.get(pk=self.kwargs['pk'])
        return self.request.user

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance != request.user and not request.user.is_superuser:
            raise PermissionDenied("У вас нет прав на удаление этого пользователя")
        self.perform_destroy(instance)
        return Response(status=status.HTTP_204_NO_CONTENT)