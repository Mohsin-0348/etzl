from django.db import models

from advertise.models.classified_model import MobilePhonesAndTablets
from advertise.choices.classified_choices import MobileTabletAccessoriesChoice, MobileOrTabletChoice


class Common(models.Model):
    model = models.CharField(max_length=32, choices=MobileOrTabletChoice.choices)
    memory = models.CharField(max_length=32, blank=True, null=True)
    color = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        abstract = True


class MobilePhone(Common, MobilePhonesAndTablets):
    pass


class MobilePhoneAccessories(MobilePhonesAndTablets):
    category = models.CharField(max_length=128, choices=MobileTabletAccessoriesChoice.choices)


class Tablets(Common, MobilePhonesAndTablets):
    pass


class OtherMobilePhoneAndTablet(MobilePhonesAndTablets):
    pass
