from django.shortcuts import render

from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import generics
from rest_framework.filters import OrderingFilter
from rest_framework.permissions import AllowAny

from users.models import Payments
from users.serializers import PaymentSerializer, UserSerializer
from rest_framework import viewsets
from users.models import CustomUser



class PaymentCreateAPIView(generics.CreateAPIView):
    serializer_class = PaymentSerializer

class PaymentListAPIView(generics.ListAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()
    filter_backends = [DjangoFilterBackend, OrderingFilter]
    filterset_fields = ("payment_method",)
    ordering_fields = ("payment_data",)


class PaymentRetrieveAPIView(generics.RetrieveAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()

class PaymentUpdateAPIView(generics.UpdateAPIView):
    serializer_class = PaymentSerializer
    queryset = Payments.objects.all()

class PaymentDeleteAPIView(generics.DestroyAPIView):
    queryset = Payments.objects.all()

class PaymentViewSet(viewsets.ModelViewSet):
    queryset = Payments.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['content_type', 'object_id']


class UserCreateAPIView(generics.CreateAPIView):
    serializer_class = UserSerializer
    queryset = CustomUser.objects.all()
    permission_classes = (AllowAny,)