from rest_framework import serializers
from users.models import Payments
from lms.serializers import LessonSerializer, CourseSerializer

class PaymentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Payments
        fields = ["id", "payment_data", "amount", "payment_method", "object_id", "user", "content_type"]