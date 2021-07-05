from django.db import transaction
from django.db.models import Q
from django.conf import settings
from django.forms.models import model_to_dict
from django.db.models import Sum
from rest_framework import status, permissions
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework.decorators import action

from flogapp.core.bases.choices import StatusChoices
from flogapp.core.bases.pagination import LimitPagination
from flogapp.core.models import PromoCode
from flogapp.core.bases import permissions as flogapp_permissions
from flogapp.accounts.choices import RoleChoices
from flogapp.accounts.models import UserPromoCode
from flogapp.accounts.serializers import UserCreateSerializer, UserSerializer
from flogapp.payments.utils import check_and_deduct_apply_promo_code_or_points
from flogapp.myfatoorah import initiate_payment, execute_payment, check_is_success
from flogapp.payments.models import ServiceRequestPayment
from .serializers import (
    ServiceSerializer,
    ServiceFeatureSerializer,
    ServiceProviderSerializer,
    ServiceProviderEmployeeSerializer,
    ServiceRequestSerializer,
    ServiceRequestAssignSerializer,
    ServiceRequestRatingSerializer
)
from .models import (
    Service,
    Feature,
    ServiceProvider,
    ServiceProviderEmployee,
    ServiceRequest,
    ServiceRequestRating,
    ServiceProviderRejectedService
)
from .choices import FieldTypeChoices, ServiceRequestStatusChoices
from .filters import ServiceFilter, ServiceFeaturerFilter, ServiceRequestFilter, ServiceProviderFilter
from .tasks import *

class ServiceViewSet(ModelViewSet):
    serializer_class = ServiceSerializer
    pagination_class = LimitPagination
    filter_class = ServiceFilter
    def get_queryset(self):
        if self.request.user.is_admin_user:
            return Service.objects.all().order_by("-created")
        else:
            return Service.objects.filter(is_active=True)
        
    def create(self, request, *args, **kwargs):
        return super(ServiceViewSet, self).create(request, *args, **kwargs)

    @action(url_path="dropdown", detail=False, methods=["GET"])
    def dropdown(self, request, *args, **kwargs):
        return Response(self.get_queryset().filter(parent__isnull=True).values('id', 'name'))
    
    
class ServiceFeaturerViewSet(ModelViewSet):
    serializer_class = ServiceFeatureSerializer
    pagination_class = LimitPagination
    filter_class = ServiceFeaturerFilter
    
    def get_queryset(self):
        qs = Feature.objects.all()
        if self.request.user.is_admin_user:
            return qs
        else:
            return qs.filter(is_active=True)

    def create(self, request, *args, **kwargs):
        return super(ServiceFeaturerViewSet, self).create(request, *args, **kwargs)

    @action(url_path="field-types", detail=False, methods=["GET"])    
    def get_field_types(self, request, *args, **kwargs):
        return Response([field.value for field in FieldTypeChoices])

    @action(url_path="activate-deactivate", detail=True, methods=["post"], permission_classes=(permissions.IsAdminUser, ))    
    def activate_deactivate(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_active = not instance.is_active
        instance.save()
        return Response({"message": "success"})

    @action(url_path="activate-deactivate-field/(?P<field_id>[0-9]+)", detail=True, methods=["post"], permission_classes=(permissions.IsAdminUser, ))    
    def activate_deactivate_field(self, request, pk, field_id, *args, **kwargs):
        instance = self.get_object()
        try:
            field = instance.service_fields.get(pk=int(field_id))
        except:
            return Response(status=status.HTTP_404_NOT_FOUND)
        field.is_active = not field.is_active
        field.save()
        return Response({"message": "success"})

    @classmethod
    def _pay(cls, request, service_request):
        CALLBACK_URL = f"{settings.BASE_URL}/service-request/payments"
        ERROR_URL = f"{settings.BASE_URL}/service-request/payments"
        print(service_request.price)
        try:
            promo_code, loylity_points, amount_discounted, discounted_price = check_and_deduct_apply_promo_code_or_points(request.user, request.data.copy(), service_request.price, service_request, PromoCode.ALL)
        except:
            promo_code, loylity_points, amount_discounted, discounted_price = check_and_deduct_apply_promo_code_or_points(request.user, request.data, service_request.price, service_request, PromoCode.ALL)
        price = discounted_price
        price_with_tax = price + service_request.tax_amount
        payment_initial = initiate_payment(price_with_tax)
        if not check_is_success(payment_initial):
            return Response(data={"paymet": "Payment initiation Failed"}, status=status.HTTP_400_BAD_REQUEST)
        user = service_request.requester or request.user
        phone = user.phone
        if phone and phone.startswith("+971"):
            phone = phone[len("+971"):]  # python9: phone.removeprefix("+971")
        data = {
            "customer_name": user.name,
            "mobile": phone,
            "email": user.email,
            "price": price_with_tax,
            "callback_url": CALLBACK_URL,
            "error_url": ERROR_URL,
            "customer_reference": "POP: Banner, SD: NA",
            "items": [{
                "item_name": user.name,
                "item_quantity": 1,
                "item_price":price,
                "tax_amount": service_request.tax_amount
            }]
        }
        payment = execute_payment(data)
        if not check_is_success(payment):
            return Response(data={"paymet": "Payment initiation Failed"}, status=status.HTTP_400_BAD_REQUEST)
        resp = {
            "payment_url": payment.get("Data", {}).get("PaymentURL"),
            "payment_id": payment.get("Data", {}).get("InvoiceTransactions", [{}])[0].get("PaymentId"),
            "invoice_id": payment.get("Data", {}).get("InvoiceId"),
        }
        user_promo_code = None
        data = {
            "service_request": service_request,
            "user": user,
            "price": discounted_price,
            "invoice_id": resp.get("invoice_id"),
            "payment_url": resp.get("payment_url"),
            "status": StatusChoices.PENDING,
            "tax_amount": service_request.tax_amount,
            "price_with_tax": price_with_tax,
            "user_promo_code": user_promo_code,
            "loylity_points": 0,
            "amount_discounted": amount_discounted or 0,
        }
        payment_obj = ServiceRequestPayment.objects.create(**data)
        if loylity_points:
            payment_obj.loylity_points = loylity_points
            LoylityPoints.check_and_create_loylity_points_entry(
                user,
                LoylityPointsChoices.SERVICE_REQUEST_PAYMENT,
                service_request,
                loylity_points
            )
        elif promo_code:
            user_promo_code = UserPromoCode.objects.create(
                user=user,
                promo_code=promo_code,
                discounted_amount=amount_discounted,
                payment_object = GenericObject.get_from_instance(payment_obj)
            )
            payment_obj.user_promo_code = user_promo_code
        payment_obj.save()
        return payment_obj
    
    def _create_service_request(self, request, service_feature, child=False):
        ser = ServiceRequestSerializer(
            data=request.data,
            context={
                "service_feature": service_feature,
                "request": request,
                "view": self
            })
        ser.is_valid(raise_exception=True)
        if child:
            fields_to_inherit = ["address", "service_feature", "requester", "primary_schedule"]
            parent = ser.validated_data["parent"]
            for field in fields_to_inherit:
                ser.validated_data[field] = getattr(parent, field)
            ser.validated_data["status"] = ServiceRequestStatusChoices.PENDING
        price = self._get_price(ser, service_feature)
        ser.validated_data["price"] = price
        instance = ser.save()
        payment_obj = self._pay(request, instance)
        if not type(payment_obj)==ServiceRequestPayment:
            return payment_obj
        data = ServiceRequestSerializer(instance, context={
            "request": request,
            "view": self
        }).data
        data["payment_url"] = payment_obj.payment_url
        if child:
            extra_hours_service_request.delay(instance.parent.id)
        return Response(data)
    
    @transaction.atomic
    @action(url_path="service-request", detail=True, methods=["POST"])    
    def service_request(self, request, pk, *args, **kwargs):
        service_feature = self.get_object()
        return self._create_service_request(request, service_feature)

    @transaction.atomic
    @action(url_path="extra-service-request", detail=True, methods=["POST"])    
    def extra_service_request(self, request, pk, *args, **kwargs):
        service_feature = self.get_object()
        if not request.data.get("parent"):
            raise ValidationError({"parent": "This field is required."})
        return self._create_service_request(request, service_feature, child=True)
    
    def _get_price(self, ser, service_feature):
        price = 0
        import decimal
        for field_name, config_field in ser.extra_fields.items():
            if config_field.is_price_unit_field:
                if config_field.field_type==FieldTypeChoices.BOOLEAN and ser.validated_data[field_name]:
                    price = price + config_field.price_per_unit
                else:
                    price = price + (config_field.price_per_unit * decimal.Decimal(ser.validated_data[field_name]))
        return price
    
    @action(url_path="get-service-request-price", detail=True, methods=["POST"])    
    def service_request_price(self, request, pk, *args, **kwargs):
        service_feature = self.get_object()
        ser_context = {
                "service_feature": service_feature,
                "request": request
            }
        ser = ServiceRequestSerializer(
            data=request.data,
            context={
                "service_feature": service_feature,
                "request": request,
                "view":self
            })
        ser.is_valid(raise_exception=True)
        price = self._get_price(ser, service_feature)
        return Response({
            "price": price,
            "tax_amount": 0,
            "price_with_tax": price
        })

    @action(url_path="dropdown", detail=False, methods=["GET"])
    def dropdown(self, request, *args, **kwargs):
        return Response(self.get_queryset().values('id', 'name', 'service__name'))
    
class ServiceProviderViewSet(ModelViewSet):
    serializer_class = ServiceProviderSerializer
    pagination_class = LimitPagination
    filter_class = ServiceProviderFilter
    def get_queryset(self):
        qs = ServiceProvider.objects.all().order_by("-created")
        if self.request.user.is_admin_user:
            return qs
        else:
            return qs.filter()

    @transaction.atomic
    @action(url_path="add-employee", detail=True, methods=["POST"])    
    def add_employee(self, request, pk, *args, **kwargs):
        service_provider = self.get_object()
        user_ser = UserCreateSerializer(data=request.data)
        user_ser.is_valid(raise_exception=True)
        user_ser.validated_data["role"] = RoleChoices.SERVICE_PROVIDER_EMPLOYEE.value
        user_ser.validated_data["roles"] = [RoleChoices.SERVICE_PROVIDER_EMPLOYEE.value]
        user = user_ser.save()
        service_provider_employee = ServiceProviderEmployee.objects.create(employee=user, service_provider=service_provider)
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

    @action(url_path="get-employees", detail=True, methods=["GET"])
    def list_employee(self, request, pk, *args, **kwargs):
        service_provider = self.get_object()
        self.filter_class = None
        return self.get_paginated_response(ServiceProviderEmployeeSerializer(
            self.paginate_queryset(self.filter_queryset(service_provider.service_provider_employees.all())), many = True, context = {"request": request}).data)
    
    
    @action(url_path="get-total-earning", detail=True, methods=["GET"], permission_classes=(permissions.IsAuthenticated, ))
    def total_earning(self, request, pk, *args, **kwargs):
        service_provider = self.get_object()
        return Response(service_provider.servicerequest_set.aggregate(total=Sum("price")))
        
class ServiceRequestViewSet(ModelViewSet):
    serializer_class = ServiceRequestSerializer
    pagination_class = LimitPagination
    filter_class = ServiceRequestFilter
    def get_queryset(self):
        qs = ServiceRequest.objects.prefetch_related('extra_service_request', 'assign').order_by("-created")
        
        if self.request.user.role==RoleChoices.SERVICE_PROVIDER:
            service_provided = self.request.user.service_provider.services.all()
            filter_q = (
                Q(
                    status=ServiceRequestStatusChoices.APPROVED, service_feature__service__in=service_provided
                )
                |
                Q(
                    assigned_service_provider=self.request.user.service_provider
                )
                |
                Q(
                    parent__assigned_service_provider=self.request.user.service_provider
                )
                |
                Q(
                    service_provider_rejected=self.request.user.service_provider
                )
            )
            qs = qs.filter(filter_q)
        elif self.request.user.role==RoleChoices.SERVICE_PROVIDER_EMPLOYEE:
            qs = qs.filter(
                assign=self.request.user
            ).exclude(
                Q(status__in=[ServiceRequestStatusChoices.PENDING, ServiceRequestStatusChoices.REJECTED, ServiceRequestStatusChoices.PAYMENT_PENDING])
            )
        elif self.request.user.role in [RoleChoices.CLIENT, RoleChoices.FREELANCER]:
            qs = qs.filter(requester=self.request.user)
        if self.action in ["list"]:
            qs = qs.filter(parent__isnull=True)
        qs = qs.select_related(
            "assigned_service_provider", "requester", "service_feature"
        ).prefetch_related(
            "suppliers_rejected",
            "assign"
        )
        return qs

    def get_serializer_context(self):
        context = super(ServiceRequestViewSet, self).get_serializer_context()
        context["service_feature"] = getattr(self, "service_feature", None)
        return context

    @action(url_path="count", detail=False, methods=["GET"], permission_classes=(permissions.IsAuthenticated,))    
    def count(self, request, *args, **kwargs):
        return Response({"count": self.get_queryset().count()})
    
    @action(url_path="approve", detail=True, methods=["PATCH"], permission_classes=(permissions.IsAdminUser,))    
    def approve(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        if service_request.status == StatusChoices.APPROVED:
            raise ValidationError({"status": "Already Approved"})
        service_request.status = StatusChoices.APPROVED
        service_request.save()
        request_approved.delay(service_request.id)
        return Response({"msg": "Service Request Approved."})

    @action(url_path="reject", detail=True, methods=["PATCH"], permission_classes=(permissions.IsAdminUser,))    
    def reject(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        if not request.data.get('rejection_reason'):
            raise ValidationError({"rejection_reason": "This field is required."})
        if service_request.status == StatusChoices.REJECTED:
            raise ValidationError({"status": "Already Reject"})
        service_request.status = StatusChoices.REJECTED
        service_request.rejection_reason = request.data["rejection_reason"]
        service_request.save()
        request_rejected.delay(service_request.id)
        return Response({"msg": "Service Request Rejected."})

    @action(url_path="supplier-accept", detail=True, methods=["PATCH"], permission_classes=(flogapp_permissions.IsServiceProvider, )) 
    def supplier_accept(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        if not service_request.status == StatusChoices.APPROVED and not service_request.parent:
            raise ValidationError({"status": "Service request is waiting for approval."})
        elif service_request.status == ServiceRequestStatusChoices.ACCEPTED:
            raise ValidationError({"status": "Service request already accepted by some other supplier."})
        service_request.assigned_service_provider = request.user.service_provider
        service_request.status = ServiceRequestStatusChoices.ACCEPTED
        service_request.save()
        if service_request.parent:
            request_extra_hours_approved.delay(service_request.id)
        else:
            request_accepted.delay(service_request.id)
        return Response({"msg": "Service Request is assigned."})

    @action(url_path="supplier-reject", detail=True, methods=["PATCH"], permission_classes=(flogapp_permissions.IsServiceProvider, ))
    def supplier_reject(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        if not service_request.status == StatusChoices.APPROVED and not service_request.parent:
            raise ValidationError({"status": "Service request is waiting for approval."})
        ServiceProviderRejectedService.objects.create(
            service_provider=request.user.service_provider,
            service_request=service_request,
            rejection_reason = request.data.get("rejection_reason", "")
        )
        service_request.service_provider_rejected.add(request.user.service_provider)
        if service_request.assigned_service_provider==request.user.service_provider:
            service_request.assigned_service_provider = None
            service_request.save()
        if service_request.parent:
            service_request.rejection_reason = request.data["rejection_reason"]
            service_request.status = ServiceRequestStatusChoices.REJECTED
            service_request.save()
            request_extra_hours_rejected.delay(service_request.id)
        return Response({"msg": "Service Request is rejected."})

    @action(url_path="mark-completed", detail=True, methods=["PATCH"])    
    def mark_completed_by_provider(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        print(service_request.status)
        if service_request.status==ServiceRequestStatusChoices.INPROGRESS:
            service_request.status = ServiceRequestStatusChoices.COMPLETED_BY_PROVIDER
            service_request.save()
            service_request_completed.delay(service_request.id)
            service_request.extra_service_request.filter(status=ServiceRequestStatusChoices.INPROGRESS).update(status = ServiceRequestStatusChoices.COMPLETED_BY_PROVIDER)
            return Response({"message": "Request marked as completed successfully."})
        raise ValidationError({"status": "Service is not in progress."})

    @action(url_path="accept-completion", detail=True, methods=["PATCH"])    
    def accept_completion(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        if service_request.status==ServiceRequestStatusChoices.COMPLETED_BY_PROVIDER:
            service_request.status = ServiceRequestStatusChoices.COMPLETED
            service_request.save()
            service_request.extra_service_request.filter(status=ServiceRequestStatusChoices.COMPLETED).update(status =ServiceRequestStatusChoices.COMPLETED)
            request_completed_by_client.delay(service_request.id)
            return Response({"message": "Request marked as completed successfully."})
        raise ValidationError({"status": "Service is not marked as completed by provider."})


    @action(url_path="mark-inprogress", detail=True, methods=["PATCH"])    
    def inprogress(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        if service_request.status==ServiceRequestStatusChoices.ACCEPTED:
            service_request.status = ServiceRequestStatusChoices.INPROGRESS
            service_request.save()
            return Response({"message": "Request marked as started successfully."})
        request_started.delay(service_request.id)
        raise ValidationError({"status": "Request is not approved."})

    
    @action(url_path="reschedule", detail=True, methods=["PATCH"])    
    def reschedule(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        ser = self.get_serializer_class()(service_request, data=request.data, context=self.get_serializer_context())
        ser.is_valid(raise_exception=True)
        ser.save()
        return Response(ser.data)
        
    @action(url_path="assign", detail=True, methods=["PATCH"])    
    def assign(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        ser = ServiceRequestAssignSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        service_request.assign.add(*ser.validated_data["assign"])
        request_assigned.delay(service_request.id, [a.id for a in ser.validated_data["assign"]])
        return Response({"message": "Employee assigned on given request."})

    @transaction.atomic
    @action(url_path="get-payment-url", detail=True, methods=["POST"])    
    def get_payment_url(self, request, pk, *args, **kwargs):
        service_request = self.get_object()
        return Response({"payment_url": ServiceFeaturerViewSet._pay(request, service_request).payment_url})

class ServiceRequestRatingViewSet(ModelViewSet):
    serializer_class = ServiceRequestRatingSerializer

    def get_queryset(self, *args, **kwargs):
        return ServiceRequestRating.objects.all()

    
