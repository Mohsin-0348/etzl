from django.db import models

from django.contrib.contenttypes.fields import GenericRelation

from rnd.models import BaseAdvertise, Category


# class CommunityChoice(models.TextChoices):
#     Services = 'Services'
#     CarLift = 'Car lift'
#     Freelancers = 'Freelancers'
#     Domestic = 'Domestic'
#     Education = 'Education'
#     Childcare = 'Childcare'
#     Classes = 'Classes'
#     Activities = 'Activities'
#     Photography = 'Photography'
#     Sports = 'Sports'
#     Music = 'Music'
#     Artists = 'Artists'


# class ServiceChoice(models.TextChoices):
#     Maids = 'Maids'
#     MoversOrRemovals = 'Movers or removals'
#     GeneralMaintenance = 'General maintenance'
#     Nannies = 'Nannies'
#     ElectronicRepair = 'Electronic repair'
#     ITRepair = 'IT repair'
#     Painters = 'Painters'
#     Plumbers = 'Plumbers'
#     Gardeners = 'Gardeners'
#     Mechanics = 'Mechanics'
#     OtherServices = 'Other services'


class Community(models.Model):
    base_advertise = GenericRelation(BaseAdvertise)

    class Meta:
        abstract = True


class Services(Community):
    pass


class CarLift(Community):
    # for car lifting
    car_lift_from = models.CharField(max_length=32, blank=True, null=True)
    car_lift_to = models.CharField(max_length=32, blank=True, null=True)


class Freelancers(Community):
    pass


class Domestic(Community):
    pass


class Education(Community):
    pass


class Childcare(Community):
    pass


class Classes(Community):
    pass


class Activities(Community):
    pass


class Photography(Community):
    pass


class Sports(Community):
    pass


class Musical(Community):
    pass


class Artists(Community):
    pass


class Others(Community):
    pass
