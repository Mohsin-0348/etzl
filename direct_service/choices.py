from django.db import models
from rest_framework import serializers

class FieldTypeChoices(models.TextChoices):
    CHAR = "CharField"
    TEXT = "TextField"
    INTEGER = "IntegerField"
    DECIMAL = "DecimalField"
    BOOLEAN = "BooleanField"
    IMAGE = "ImageField"
    FILE = "FileField"
    DATE = "DateField"
    DATETIME = "DateTimeField"
    DURATION = "DurationField"

class ServiceRequestStatusChoices(models.TextChoices):
    PAYMENT_PENDING = "payment-pending"
    PENDING = 'pending'
    APPROVED = 'approved'
    REJECTED = 'rejected'
    ACCEPTED = "accepted"
    INPROGRESS = 'inprogress'
    COMPLETED_BY_PROVIDER = 'completed-by-provider'
    COMPLETED = 'completed'
    
class ServiceRequestRatingTypeChoices(models.TextChoices):
    FROM_EMPLOYEE = "from-employee"
    FROM_CLIENT = "from-client"
    
FieldTypeChoicesFieldMap = {
    FieldTypeChoices.CHAR.value: serializers.CharField(max_length=500),
    FieldTypeChoices.TEXT.value: serializers.CharField(),
    FieldTypeChoices.INTEGER.value: serializers.IntegerField(), 
    FieldTypeChoices.DECIMAL.value: serializers.DecimalField(max_digits=6, decimal_places=2),
    FieldTypeChoices.BOOLEAN.value: serializers.BooleanField(),
    FieldTypeChoices.IMAGE.value: serializers.ImageField(),
    FieldTypeChoices.FILE.value: serializers.FileField(),
    FieldTypeChoices.DATE.value: serializers.DateField(),
    FieldTypeChoices.DATETIME.value: serializers.DateTimeField(),
    FieldTypeChoices.DURATION.value: serializers.DurationField()
}
