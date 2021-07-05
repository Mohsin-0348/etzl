import decimal
from django.db import models
from django.conf import settings


class BaseModel(models.Model):
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class BasePriceModel(BaseModel):
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_with_tax = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    tax_percentage = models.DecimalField(max_digits=10, decimal_places=2,)
                                         # default=decimal.Decimal(settings.VAT_PERCENTAGE))
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        abstract = True

    # def save(self, *args, **kwargs):
    #     print("inside save")
    #     self.tax_percentage = settings.VAT_PERCENTAGE
    #     self.tax_amount = decimal.Decimal(self.price) * decimal.Decimal((settings.VAT_PERCENTAGE / 100))
    #     self.price_with_tax = decimal.Decimal(self.price) + self.tax_amount
    #     super(BasePriceModel, self).save(*args, **kwargs)


