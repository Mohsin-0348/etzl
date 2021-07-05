from django.db import models
from django.contrib.auth import get_user_model

from bases.models import BaseModel

User = get_user_model()


class CityChoice(models.TextChoices):
    Addis_Ababa = 'Addis ababa'
    Mekelle = 'Mekelle'
    Gondar = 'Gondar'
    Adama = 'Adama'
    Awassa = 'Awassa'
    Bahir_Dar = 'Bahir dar'
    Dire_Dawa = 'Dire dawa'
    Sodo = 'Sodo'
    Dessie = 'Dessie'
    Jimma = 'Jimma'
    Jijiga = 'Jijiga'
    Shashemene = 'Shashemene'
    Bishoftu = 'Bishoftu'
    ArbaMinch = 'Arba minch'
    Hosana = 'Hosana'
    Harar = 'Harar'
    Dilla = 'Dilla'
    Debre_Birhan = 'Debre birhan'
    Asella = 'Asella'
    DebreMarqos = 'Debre marqos'
    Kombolcha = 'Kombolcha'
    DebreTabor = 'Debre tabor'
    Adigrat = 'Adigrat'
    Weldiya = 'Weldiya'
    Sebeta = 'Sebeta'
    Ambo = 'Ambo'
    Arsi = 'Arsi'
    Gurage = 'Gurage'
    Gambella = 'Gambella'


class City(models.Model):
    city = models.CharField(max_length=32, choices=CityChoice.choices)

    class Meta:
        verbose_name_plural = 'Cities'


class AdvertiseBase(models.Model):
    type = models.CharField(max_length=32)


class BaseAdvertise(BaseModel):
    user = models.ForeignKey(User, on_delete=models.DO_NOTHING, related_name="posted_user")
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=16, decimal_places=2)
    location = models.CharField(max_length=100, blank=True, null=False)
    availability = models.BooleanField(default=True)

    class Meta:
        abstract = True
