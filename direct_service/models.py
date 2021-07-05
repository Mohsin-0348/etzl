from django.utils import timezone
from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator
from django_mysql.models import ListCharField
from autoslug import AutoSlugField
from flogapp.core.bases.models import BaseModel, BaseStatusModel, BasePriceModel
from flogapp.accounts.choices import RoleChoices, CurrentCityChoices
from .choices import FieldTypeChoices, ServiceRequestStatusChoices, ServiceRequestRatingTypeChoices
from .utils import upload_licence_path, upload_passport_path, upload_contract_info_path, upload_residance_photo_path


def custom_slugify(self):
    return self.upper()


def get_request_id(self):
    serial = 1
    try:
        request_object = ServiceRequest.objects.filter(created__date=timezone.now().date()).latest('created')
        serial = int(request_object.serial[-4:]) + 1
        print(serial)
    except ServiceRequest.DoesNotExist:
        pass
    return "{}-{}-{:04d}".format(
        "FLGP", self.created.strftime("%Y%m%d"), serial
    )


class Service(BaseModel):
    name = models.CharField(max_length=200)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name="sub_services")
    cover_photo = models.ImageField(upload_to='services')
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)


class Feature(BaseModel):
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    name = models.CharField(max_length=200)
    cover_photo = models.ImageField(upload_to='services')
    description = models.TextField(blank=True)
    # price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)
    cities = ListCharField(
        base_field=models.CharField(max_length=50, choices=CurrentCityChoices.choices),
        max_length=1000
    )


class ServiceField(BaseModel):
    service_feature = models.ForeignKey(Feature, on_delete=models.DO_NOTHING, related_name="service_fields")
    field_name = models.SlugField(max_length=200)
    label = models.TextField()
    field_type = models.CharField(max_length=200, choices=FieldTypeChoices.choices)
    is_price_unit_field = models.BooleanField(default=False)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    is_required = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ("service_feature", "field_name")


class ServiceProvider(BaseModel):
    name = models.CharField(max_length=200)
    cover_photo = models.ImageField(upload_to='services')
    description = models.TextField(blank=True)
    user = models.OneToOneField("accounts.User", on_delete=models.DO_NOTHING, related_name="service_provider")
    services = models.ManyToManyField(Service, through="services.ServiceProviderService")
    licence = models.FileField(upload_to=upload_licence_path)
    passport = models.FileField(upload_to=upload_passport_path)
    licence_start = models.DateField()
    licence_end = models.DateField()
    residence_photo = models.ImageField(upload_to=upload_residance_photo_path)
    contract_info = models.FileField(upload_to=upload_contract_info_path)
    cities = ListCharField(
        base_field=models.CharField(max_length=50, choices=CurrentCityChoices.choices),
        max_length=1000
    )


class ServiceProviderEmployee(BaseModel):
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.DO_NOTHING,
                                         related_name="service_provider_employees")
    employee = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="service_provider_employee")
    is_active = models.BooleanField(default=True)


class ServiceProviderService(BaseModel):
    service = models.ForeignKey(Service, on_delete=models.DO_NOTHING)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.DO_NOTHING)
    price_per_unit = models.DecimalField(max_digits=10, decimal_places=2)
    is_active = models.BooleanField(default=True)


class ServiceRequest(BasePriceModel):
    serial = AutoSlugField(
        populate_from=get_request_id, null=True, db_index=True, slugify=custom_slugify
    )
    service_feature = models.ForeignKey(Feature, on_delete=models.DO_NOTHING)
    status = models.CharField(max_length=25, choices=ServiceRequestStatusChoices.choices,
                              default=ServiceRequestStatusChoices.PAYMENT_PENDING)
    requester = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING, related_name="requested_services")
    address = models.ForeignKey("accounts.Address", on_delete=models.DO_NOTHING,
                                related_name="requested_services_addresss")
    primary_schedule = models.DateTimeField()
    secondary_schedule = models.DateTimeField(null=True)
    description = models.TextField(blank=True)
    audio_note = models.FileField(upload_to='direct_service/audio_notes', blank=True, null=True)
    rejection_reason = models.TextField(null=True)
    assigned_service_provider = models.ForeignKey(ServiceProvider, on_delete=models.DO_NOTHING, null=True)
    service_provider_rejected = models.ManyToManyField(ServiceProvider,
                                                       through="services.ServiceProviderRejectedService", blank=True,
                                                       related_name="rejected_requests")
    assign = models.ManyToManyField("accounts.User", blank=True)
    parent = models.ForeignKey('self', null=True, on_delete=models.CASCADE, related_name="extra_service_request")


class ServiceProviderRejectedService(BaseModel):
    service_request = models.ForeignKey(ServiceRequest, related_name="suppliers_rejected", on_delete=models.DO_NOTHING)
    service_provider = models.ForeignKey(ServiceProvider, on_delete=models.DO_NOTHING)
    rejection_reason = models.TextField(null=True)


class ServiceRequestAttachments(BaseModel):
    service_request = models.ForeignKey(ServiceRequest, related_name="attachments", on_delete=models.DO_NOTHING)
    attachment = models.FileField(upload_to='direct_service/attachments')


class ServiceRequestValues(BaseModel):
    service_request = models.ForeignKey(ServiceRequest, related_name="values", on_delete=models.DO_NOTHING)
    service_field = models.ForeignKey(ServiceField, on_delete=models.DO_NOTHING)
    value = models.CharField(max_length=200)


class ServiceRequestRating(BaseModel):
    service_request = models.ForeignKey(ServiceRequest, related_name="ratings", on_delete=models.DO_NOTHING)
    rating_from = models.CharField(max_length=25, choices=RoleChoices.choices)
    created_by = models.ForeignKey("accounts.User", on_delete=models.DO_NOTHING,
                                   related_name="ratings_for_service_request")
    description = models.TextField(blank=True)
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
