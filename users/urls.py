from users.apps import UsersConfig
from rest_framework.routers import DefaultRouter
from users.views import  PaymentCreateAPIView, PaymentListAPIView, PaymentRetrieveAPIView, PaymentUpdateAPIView, PaymentDeleteAPIView
from django.urls import path

app_name = "users"

# router = DefaultRouter()
# router.register(r"courses", CourseViewSet, basename="payment")


urlpatterns = [
    path("payment/create/", PaymentCreateAPIView.as_view(), name="payment-create"),
    path("payment/", PaymentListAPIView.as_view(), name="payment-list"),
    path("payment/<int:pk>/", PaymentRetrieveAPIView.as_view(), name="payment"),
    path("payment/update/<int:pk>/", PaymentUpdateAPIView.as_view(), name="payment-update"),
    path("payment/delete/<int:pk>/", PaymentDeleteAPIView.as_view(), name="payment-delete"),

] #+ router.urls
