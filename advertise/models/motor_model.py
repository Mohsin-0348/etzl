from django.db import models
from django.core.validators import MinValueValidator
from django.contrib.contenttypes.fields import GenericRelation

from rnd.models import Category, BaseAdvertise


class MotorChoice(models.TextChoices):
    CAR = 'Car'
    MOTORCYCLE = 'MotorCycle'
    AUTO_ACCESSORIES_AND_PARTS = 'AutoAccessoriesAndParts'
    HEAVY_VEHICLES = 'Heavy vehicles'


class Motors(models.Model):
    # base = models.ForeignKey(Category, on_delete=models.DO_NOTHING)
    # types = models.CharField(max_length=32, choices=MotorChoice.choices)
    # motor fields
    seller_type = models.CharField(max_length=64, blank=True, null=True)
    usage = models.CharField(max_length=64, blank=True, null=True)

    class Meta:
        abstract = True


class Car(Motors):
    # base = models.ForeignKey(Motors, on_delete=models.DO_NOTHING)
    # car fields
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    trim = models.CharField(max_length=64, blank=True, null=True)
    regional_specs = models.CharField(max_length=64)
    body_condition = models.CharField(max_length=64)
    mechanic_condition = models.CharField(max_length=64)
    year = models.PositiveIntegerField(blank=True, null=True)
    body_type = models.CharField(max_length=64, blank=True, null=True)
    doors = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    mileage = models.PositiveIntegerField(blank=True, null=True)
    staring_side = models.CharField(max_length=64, blank=True, null=True)
    fuel_type = models.CharField(max_length=64, blank=True, null=True)
    no_of_cylinder = models.CharField(max_length=32)
    horse_power = models.CharField(max_length=32)
    transmission_type = models.CharField(max_length=32)
    insurance = models.CharField(max_length=64, blank=True, null=True)

    # extra information
    climate_control = models.BooleanField(default=False)
    cooled_seats = models.BooleanField(default=False)
    dvd_player = models.BooleanField(default=False)
    front_heel_drive = models.BooleanField(default=False)
    keyless_entry = models.BooleanField(default=False)
    leather_seats = models.BooleanField(default=False)
    navigation_system = models.BooleanField(default=False)
    parking_sensors = models.BooleanField(default=False)
    premium_sound_system = models.BooleanField(default=False)
    rear_view_camera = models.BooleanField(default=False)

    base_advertise = GenericRelation(BaseAdvertise)


class MotorCycle(Motors):
    # base = models.ForeignKey(Motors, on_delete=models.DO_NOTHING)
    # category = models.CharField(max_length=128)
    # sub_category = models.CharField(max_length=128)
    # motor cycle fields
    condition = models.CharField(max_length=64, blank=True, null=True)
    mileage = models.PositiveIntegerField(blank=True, null=True)
    year = models.PositiveIntegerField(blank=True, null=True)
    final_drive_system = models.CharField(max_length=64, blank=True, null=True)
    wheels = models.CharField(max_length=64, blank=True, null=True)
    manufacturer = models.CharField(max_length=64, blank=True, null=True)
    engine_size = models.CharField(max_length=64, blank=True, null=True)
    warranty = models.CharField(max_length=64, blank=True, null=True)
    color = models.CharField(max_length=64, blank=True, null=True)

    base_advertise = GenericRelation(BaseAdvertise)


class AutoAccessoriesAndParts(Motors):
    # base = models.ForeignKey(Motors, on_delete=models.DO_NOTHING)
    # category = models.CharField(max_length=128)
    # sub_category = models.CharField(max_length=128)
    # auto accessories and parts fields
    condition = models.CharField(max_length=64, blank=True, null=True)

    base_advertise = GenericRelation(BaseAdvertise)


class HeavyVehicles(Motors):
    # base = models.ForeignKey(Motors, on_delete=models.DO_NOTHING)
    # category = models.CharField(max_length=128)
    # sub_category = models.CharField(max_length=128)
    # heavy vehicle fields
    brand = models.CharField(max_length=64)
    model = models.CharField(max_length=64)
    mileage = models.PositiveIntegerField(blank=True, null=True)
    body_condition = models.CharField(max_length=64)
    mechanic_condition = models.CharField(max_length=64)
    year = models.PositiveIntegerField(blank=True, null=True)
    warranty = models.CharField(max_length=64, blank=True, null=True)
    capacity_or_weight = models.CharField(max_length=64, blank=True, null=True)
    no_of_cylinder = models.CharField(max_length=32)
    horse_power = models.CharField(max_length=32)
    fuel_type = models.CharField(max_length=64, blank=True, null=True)

    base_advertise = GenericRelation(BaseAdvertise)


class OtherMotors(Motors):
    base_advertise = GenericRelation(BaseAdvertise)


# class Boats(BaseAdvertise):
#     base = models.ForeignKey(Motors, on_delete=models.DO_NOTHING)
#     category = models.CharField(max_length=128)
#     sub_category = models.CharField(max_length=128)
#     # boats fields
#     seller_type = models.CharField(max_length=64, blank=True, null=True)
#     condition = models.CharField(max_length=64, blank=True, null=True)
#     usage = models.CharField(max_length=64, blank=True, null=True)
#     length = models.CharField(max_length=64, blank=True, null=True)
#     warranty = models.CharField(max_length=64, blank=True, null=True)
#     color = models.CharField(max_length=64, blank=True, null=True)
#
#
# class NumberPlates(BaseAdvertise):
#     base = models.ForeignKey(Motors, on_delete=models.DO_NOTHING)
#     category = models.CharField(max_length=128)
#     sub_category = models.CharField(max_length=128)
#     # number plates fields
