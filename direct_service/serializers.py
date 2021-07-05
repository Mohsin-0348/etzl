import json
import copy
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.storage import get_storage_class
from rest_framework import serializers
from rest_framework.permissions import SAFE_METHODS
from rest_framework.exceptions import ValidationError
from flogapp.accounts.choices import RoleChoices
from flogapp.accounts.models import Address
from flogapp.payments.models import ServiceRequestPayment
from flogapp.payments.choices import PaymentStatusChoices

from .models import (
    Service,
    Feature,
    ServiceField,
    ServiceProvider,
    ServiceProviderService,
    ServiceProviderEmployee,
    ServiceRequest,
    ServiceRequestValues,
    ServiceRequestRating,
    ServiceRequestAttachments,
    ServiceProviderRejectedService
)
from flogapp.accounts.serializers import UserSerializer, UserCreateSerializer, AddressSerializer
from .choices import FieldTypeChoices, FieldTypeChoicesFieldMap, ServiceRequestRatingTypeChoices, ServiceRequestStatusChoices
from .tasks import *

class ServiceSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    has_child_services = serializers.SerializerMethodField()

    def get_has_child_services(self, obj):
        return obj.sub_services.exists()
    
    class Meta:
        model = Service
        fields = "__all__"
    
class ServiceFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceField
        fields = "__all__"
        extra_kwargs = {"service_feature": {"required":False}}

    
class ServiceFieldSerializerForValidation(serializers.Serializer):
    field_name = serializers.RegexField("[a-zA-Z0-9_-]+")
    label = serializers.CharField(max_length=200)
    field_type = serializers.ChoiceField(choices=FieldTypeChoices)
    is_price_unit_field = serializers.BooleanField(default=False)
    is_active = serializers.BooleanField(default=True)
    is_required = serializers.BooleanField(default=True)
    price_per_unit = serializers.DecimalField(max_digits=10, decimal_places=2, min_value=0, allow_null=True, default=None)
    
    def validate(self, data):
        if data["is_price_unit_field"] and data["price_per_unit"] is None:
            raise ValidationError({"price_per_unit": "This value can't be null for price unit fields"})
        return data

class ServiceFields(serializers.Field):    
    def to_internal_value(self, data):
        data = json.loads(data)
        ser = ServiceFieldSerializerForValidation(data=data, many=True)
        ser.is_valid(raise_exception=True)
        if not any([row.get("is_price_unit_field", False) for row in ser.validated_data ]):
            raise ValidationError("One field must be marked as price unit field")
        return ser.validated_data
    
    def to_representation(self, obj):
        return ServiceFieldSerializer(obj.all(), many=True).data

class ServiceFeatureSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    service_fields = ServiceFields(write_only=False)
    price_unit_fields = [FieldTypeChoices.INTEGER, FieldTypeChoices.DECIMAL, FieldTypeChoices.BOOLEAN]
    class Meta:
        model = Feature
        fields = "__all__"
        
    def validate(self, data):
        has_price_unit_field = False
        for field in data["service_fields"]:
            if field.get("is_price_unit_field") and field.get("field_type") not in self.price_unit_fields:
                raise ValidationError({field["field_name"]:"Price unit field can be only numberic types."})                
            has_price_unit_field = has_price_unit_field or field.get("is_price_unit_field", False)
        if not has_price_unit_field:
            raise ValidationError({"is_price_unit_field": "Please mark one or more field as price unit field."})
        return data
    
    @transaction.atomic
    def create(self, validated_data, *args, **kwargs):
        service_fields = validated_data.pop("service_fields")
        instance = super(ServiceFeatureSerializer, self).create(validated_data, *args, **kwargs)
        service_fields_objs = []
        for service_field in service_fields:
            service_fields_objs.append(ServiceField(service_feature=instance, **service_field))
        ServiceField.objects.bulk_create(service_fields_objs)
        return instance

    @transaction.atomic
    def update(self, instance, validated_data, *args, **kwargs):
        service_fields = validated_data.pop("service_fields")
        instance = super(ServiceFeatureSerializer, self).update(instance, validated_data, *args, **kwargs)
        service_fields_objs_to_create = []
        service_fields_objs_to_update = []
        for service_field in service_fields:
            try:
                field = ServiceField.objects.get(
                    field_name=service_field["field_name"], service_feature=instance
                )
                field.label = service_field["label"]
                field.is_active = service_field.get("is_active", True)
                service_fields_objs_to_update.append(field)
            except ServiceField.DoesNotExist:
                service_fields_objs_to_create.append(ServiceField(service_feature=instance, **service_field))
        ServiceField.objects.bulk_create(service_fields_objs_to_create)
        ServiceField.objects.bulk_update(service_fields_objs_to_update, ["label", "is_active"])
        return instance
    
class ServiceProviderSerializer(serializers.ModelSerializer):
    is_active = serializers.BooleanField(default=True)
    
    class Meta:
        model = ServiceProvider
        fields = "__all__"


class SupplierUserField(serializers.Field):    
    def to_internal_value(self, data):
        data = json.loads(data)
        instance = getattr(self, "instance", None)
        if instance and data["email"]==instance.email:
            del data["email"]
        if instance and data["phone"]==instance.phone:
            del data["phone"]
        print(data)
        ser = UserCreateSerializer(instance=instance, data=data, partial=bool(instance))
        ser.is_valid(raise_exception=True)
        #if not instance:
        #    ser.validated_data["registered_as"] = RoleChoices.SERVICE_PROVIDER_EMPLOYEE.value
        return ser.validated_data

    def to_representation(self, obj):
        return UserSerializer(obj).data

class ServiceProviderSerializer(serializers.ModelSerializer):
    user = SupplierUserField()
    
    class Meta:
        model = ServiceProvider
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        if kwargs["context"]["request"].method not in SAFE_METHODS:
            self.fields["services"] = serializers.PrimaryKeyRelatedField(
                queryset=Service.objects.filter(parent__isnull=True),
                allow_null=False,
                many=True,
                write_only=True
            )
        else:
            self.fields["services"] = serializers.SerializerMethodField()
        if kwargs["context"]["request"].method=="PATCH":
            self.fields["user"].instance = args[0].user 
        return super(ServiceProviderSerializer, self).__init__(*args, **kwargs)
    def validate(self, data):
        if not data["services"]:
            raise ValidationError({"services": "This fiels can not be blank."})
        return data

    def get_services(self, obj):
        return obj.services.values("id", "name")

    @transaction.atomic
    def create(self, validated_data, *args, **kwargs):
        user = validated_data.pop("user")
        user['role'] = RoleChoices.SERVICE_PROVIDER.value
        user["roles"] = [RoleChoices.SERVICE_PROVIDER.value]
        services = validated_data.pop("services")
        user = UserCreateSerializer().create(user)
        validated_data["user"] = user
        instance = super(ServiceProviderSerializer, self).create(validated_data, *args, **kwargs)
        objs = []
        for service in services:
            objs.append(ServiceProviderService(service=service, service_provider=instance, price_per_unit=0))
        ServiceProviderService.objects.bulk_create(objs)
        return instance
    
    @transaction.atomic
    def update(self, instance, validated_data, *args, **kwargs):
        user = validated_data.pop("user")
        services = validated_data.pop("services")
        user = UserCreateSerializer(instance.user, data=user, partial=True)
        user.is_valid(raise_exception=True)
        user = user.save()
        validated_data["user"] = user
        instance = super(ServiceProviderSerializer, self).update(instance, validated_data, *args, **kwargs)
        objs = []
        for service in services:
            ServiceProviderService.objects.update_or_create(service=service, service_provider=instance, defaults={"price_per_unit":0})
        ServiceProviderService.objects.exclude(service__in=services).delete()
        return instance

    def to_representation(self, obj):
        ret = super(ServiceProviderSerializer, self).to_representation(obj)
        print(self.context["view"].action)
        if self.context.get("view") and self.context["view"].action=="retrieve":
            ret["request_accepted"] = ServiceRequest.objects.filter(
                assigned_service_provider=obj,
                parent__isnull=True
            ).count()
            ret["request_rejected"] =  ServiceRequest.objects.filter(
                service_provider_rejected=obj,
                parent__isnull=True
            ).count()
        return ret
    
class ServiceProviderEmployeeSerializer(serializers.ModelSerializer):
    employee = UserSerializer()
    class Meta:
        model = ServiceProviderEmployee
        fields = "__all__"

class ServiceRequestValuesSerializer(serializers.ModelSerializer):
    service_field = ServiceFieldSerializer()
    class Meta:
        model = ServiceRequestValues
        fields = "__all__"

    def to_representation(self, obj):
        ret = super(ServiceRequestValuesSerializer, self).to_representation(obj)
        if obj.service_field.field_type in [FieldTypeChoices.FILE, FieldTypeChoices.IMAGE]:
            ret["value"] = self.context["request"].build_absolute_uri(settings.MEDIA_URL+ret["value"])
        return ret

class ServiceRequestAddressField(serializers.Field):    
    def to_internal_value(self, data):
        data = json.loads(data)
        if type(data)==int:
            return Address.objects.get(id=data)
        data["user"] = self.context["request"].user.id
        ser = AddressSerializer(data=data)
        ser.is_valid(raise_exception=True)
        return ser.validated_data

    def to_representation(self, obj):
        return AddressSerializer(obj).data

class ServiceRequestSerializer(serializers.ModelSerializer):
    work_history = [
        {
            "type": "payment-successfull",
            "title": "Payment done",
            "status": ServiceRequestStatusChoices.PENDING,
            "done": False
        },
        {
            "type": "approved",
            "title":"Service Request Approved",
            "status": ServiceRequestStatusChoices.APPROVED,
            "done": False
        },
        {
            "type": "accepted",
            "title":"Supplier Accepted",
            "status": ServiceRequestStatusChoices.ACCEPTED,
            "done": False
        },
        {
            "type": "inprogress",
            "title":"Service Request in progress",
            "status": ServiceRequestStatusChoices.INPROGRESS,
            "done": False
        },
        {
            "type": "completed-by-provider",
            "title":"Service Request Completed By Service Provider",
            "status": ServiceRequestStatusChoices.COMPLETED_BY_PROVIDER,
            "done": False
        },
        {
            "type": "completed",
            "title":"Service Request Completed",
            "status": ServiceRequestStatusChoices.COMPLETED,
            "done": False
        }
    ]
    extra_request_history = [
        {
            "type": "pending",
            "title":"Supplier Accepted",
            "status": ServiceRequestStatusChoices.PENDING,
            "done": False
        },
        {
            "type": "payment-done",
            "title":"Extra Service Request Payment Done",
            "status": ServiceRequestStatusChoices.INPROGRESS,
            "done": False
        }
    ]
    def get_extra_request(self, obj):
        qs = obj.extra_service_request.all()
        if self.context["request"].user.role==RoleChoices.SERVICE_PROVIDER_EMPLOYEE:
            qs = qs.filter(status=ServiceRequestStatusChoices.INPROGRESS)
        return ServiceRequestSerializer(qs, many=True, context=self.context).data
    
    def __init__(self, *args, **kwargs):
        is_get_price_view = kwargs["context"]["view"].action in ["service_request_price", "extra_service_request"]
        if is_get_price_view:
            self.Meta.extra_kwargs.update({
                "primary_schedule": {"required": False},
                "service_feature": {"required": False},
                "requester": {"required": False}
            })
        if kwargs["context"]["view"].action=="reschedule":
            self.Meta.fields = ("primary_schedule", "secondary_schedule")
        else:
            self.Meta.fields = "__all__"
            self.fields["extra_request"] = serializers.SerializerMethodField()
            self.fields["attachments"] = serializers.ListField(
                child=serializers.FileField(
                    max_length=100000,
                    allow_empty_file=False
                ), write_only=True,required=False
            )
            self.fields["address"] = ServiceRequestAddressField(required=not is_get_price_view)
            if kwargs["context"]["request"].method.lower()=='post' and kwargs["context"].get("service_feature"):
                service_feature = kwargs["context"]["service_feature"]
                self.extra_fields = {}
                from copy import deepcopy
                fields_qs = service_feature.service_fields.all()
                if is_get_price_view:
                    fields_qs = fields_qs.filter(is_price_unit_field=True)
                self.fields["attachments"] = serializers.ListField(
                    child=serializers.FileField(
                        max_length=100000,
                        allow_empty_file=False
                    ), write_only=True,required=False
                )
                for service_field in fields_qs:
                    self.extra_fields[service_field.field_name] = service_field
                    self.fields[service_field.field_name] = deepcopy(FieldTypeChoicesFieldMap[service_field.field_type])
                    self.fields[service_field.field_name].required = service_field.is_required
                    if service_field.field_type in [FieldTypeChoices.FILE, FieldTypeChoices.IMAGE]:
                        self.fields[service_field.field_name].use_url = True
                    self.fields[service_field.field_name].write_only = True
            else:
                self.fields["values"] = ServiceRequestValuesSerializer(many=True)
                self.fields["attachments"] = ServiceRequestAttachmentsSerializer(many=True, context=kwargs["context"])
        return super(ServiceRequestSerializer, self).__init__(*args, **kwargs)
        
    class Meta:
        model = ServiceRequest
        fields = "__all__"
        extra_kwargs = {
            "price":{"read_only":True}
        }
        
    def validate(self, data):
        if (
                self.context["view"].action=="reschedule" 
                and (self.instance.primary_schedule - timezone.now()).total_seconds()<7200
                and (data["primary_schedule"] - timezone.now()).total_seconds()<7200
        ):
            raise ValidationError({"primary_schedule": "Only reschedule request before 2 hours."})
        return data
    
    @transaction.atomic        
    def create(self, validated_data, *args, **kwargs):
        extra_fields_objs = []
        address = validated_data.get("address")
        if not type(address) == Address:
            validated_data["address"] = Address.objects.create(**address)
        storage = get_storage_class()()
        for field_name, field_instance in self.extra_fields.items():
            if field_name in validated_data.keys():
                if field_instance.field_type in [FieldTypeChoices.FILE, FieldTypeChoices.IMAGE]:
                    f = validated_data.get(field_name)
                    validated_data[field_name] = storage.save(name="direct_service/values/"+f.name, content=f)
                extra_fields_objs.append(ServiceRequestValues(
                    service_field = field_instance,
                value = validated_data.pop(field_name)
            ))
        attachments = validated_data.pop("attachments", [])
        instance = super(ServiceRequestSerializer, self).create(validated_data, *args, **kwargs)
        for attachment in attachments:
            ServiceRequestAttachments.objects.create(attachment=attachment, service_request=instance)
        for extra_field in extra_fields_objs:
            extra_field.service_request = instance
        ServiceRequestValues.objects.bulk_create(extra_fields_objs)
        return instance
    
    def _get_work_history(self, ret):
        history = []
        extra_request_history = copy.deepcopy(self.extra_request_history)
        if not ret["parent"]:
            work_history = copy.deepcopy(self.work_history)
            index = next((index for (index, d) in enumerate(work_history) if d["status"] == ret["status"]), None)
            if index is not None:
                for wh in work_history[:index+1]:
                    wh["done"] = True
                    history.append(wh)
                history = history + work_history[index+1:]
            else:
                history = work_history
            if index and ret['status']==ServiceRequestStatusChoices.COMPLETED:
                history[-1]["done"] = True
            extra_list = []
            for e in ret["extra_request"]:
                extra_list+=e["request_history"]
            history = history[:-1] + extra_list + [history[-1]]
        else:
            if ret["status"] in [ServiceRequestStatusChoices.INPROGRESS, ServiceRequestStatusChoices.COMPLETED_BY_PROVIDER, ServiceRequestStatusChoices.COMPLETED]:
                extra_request_history[0]["done"] = True
                extra_request_history[1]["done"] = True
            elif ret["status"]==ServiceRequestStatusChoices.ACCEPTED:
                extra_request_history[0]["done"] = True
            history = extra_request_history
        return history
            
    def to_representation(self, obj):
        ret = super(ServiceRequestSerializer, self).to_representation(obj)
        ret["service_feature"] = ServiceFeatureSerializer(obj.service_feature, context=self.context).data
        ret["assign"] = [
            {
                "id": a.id,
                "name": a.name,
                "photo": a.photo.path if a.photo else None,
                "phone": a.phone,
                "email": a.email,
            }
            for a in obj.assign.all()
        ]
        #print(self.context["view"].action)
        if self.context.get("view") and self.context["view"].action=="retrieve":
            ret["request_history"] = self._get_work_history(ret)
            ret["payments"] = [{
                "id": payment.id,
                "price": payment.price
            }for payment in ServiceRequestPayment.objects.filter(status=PaymentStatusChoices.COMPLETE).filter(
                service_request=obj
            )]
        ret["requester"] = {
            "id":obj.requester.id,
            "name": obj.requester.name,
            "phone": obj.requester.phone,
            "email": obj.requester.email
        }
        if self.context.get("request") and self.context["request"].user.role==RoleChoices.SERVICE_PROVIDER:
            ret["is_rejected"] = self.context["request"].user.service_provider.id in ret["service_provider_rejected"]
        ret["service_provider_rejected"] = ServiceProviderRejectedServiceSerializer(obj.suppliers_rejected.all(), many=True).data
        if obj.assigned_service_provider:
            ret["assigned_service_provider"] = {
                "id": obj.assigned_service_provider.id,
                "name": obj.assigned_service_provider.name
            }
        return ret

class ServiceProviderRejectedServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceProviderRejectedService
        fields = "__all__"
    def to_representation(self, obj):
        ret = super(ServiceProviderRejectedServiceSerializer, self).to_representation(obj)
        ret["supplier_name"] = obj.service_provider.name
        return ret

class ServiceRequestAttachmentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestAttachments
        fields = "__all__"
        
class ServiceRequestAssignSerializer(serializers.Serializer):
    assign = serializers.PrimaryKeyRelatedField(queryset=get_user_model().objects.filter(roles__in=[RoleChoices.SERVICE_PROVIDER_EMPLOYEE]), many=True)

    def validate_assign(self, assign):
        if not len(assign):
            raise ValidationError("Assign list can not be empty.")
        return assign


class ServiceRequestRatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceRequestRating
        fields = "__all__"
        extra_kwargs = {
            "created_by": {"read_only": True},
            "rating_from": {"read_only": True}
            
        }

    def create(self, validated_data, *args, **kwargs):
        user = self.context["request"].user
        validated_data["created_by"] = user
        validated_data["rating_from"] = user.role
        return super(ServiceRequestRatingSerializer, self).create(validated_data, *args, **kwargs)
