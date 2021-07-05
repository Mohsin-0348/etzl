from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from rnd.models import Category, BaseAdvertise
from advertise.choices.classified_choices import ClassifiedChoice


class Classified(models.Model):
    base_advertise = GenericRelation(BaseAdvertise)
    # classified fields


class Electronics(Classified):
    category = models.CharField(max_length=128)
    sub_category = models.CharField(max_length=128)
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    warranty = models.CharField(max_length=32, blank=True, null=True)


class ComputersAndNetworking(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    brand = models.CharField(max_length=32)
    warranty = models.CharField(max_length=32, blank=True, null=True)

    abstract = True


class BusinessAndIndustrial(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class HomeAppliances(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    brand = models.CharField(max_length=32)


class SportsEquipment(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class ClothingAndAccessories(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class CamerasAndImaging(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    brand = models.CharField(max_length=32)
    warranty = models.CharField(max_length=32, blank=True, null=True)


class JewelryAndWatches(models.Model):
    base = models.ForeignKey(Classified, on_delete=models.DO_NOTHING)
    category = models.CharField(max_length=128)
    sub_category = models.CharField(max_length=128)
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)

    # extra information
    amber = models.BooleanField(default=False)
    beads = models.BooleanField(default=False)
    bronze = models.BooleanField(default=False)
    ceramic = models.BooleanField(default=False)
    crystal = models.BooleanField(default=False)
    cz = models.BooleanField(default=False)
    diamond = models.BooleanField(default=False)
    gemstone = models.BooleanField(default=False)
    leather = models.BooleanField(default=False)
    plastic = models.BooleanField(default=False)
    platinum = models.BooleanField(default=False)
    rhinestones = models.BooleanField(default=False)
    rubber = models.BooleanField(default=False)
    semi_precious_or_birth_stones = models.BooleanField(default=False)
    shell_bone_coral = models.BooleanField(default=False)
    silver = models.BooleanField(default=False)
    steel = models.BooleanField(default=False)
    titanium = models.BooleanField(default=False)
    white_gold = models.BooleanField(default=False)
    wood = models.BooleanField(default=False)
    yellow_gold = models.BooleanField(default=False)
    other_material = models.BooleanField(default=False)
    other_metal = models.BooleanField(default=False)


class MusicalInstruments(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    brand = models.CharField(max_length=32)


class Gaming(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    package = models.CharField(max_length=32, blank=True, null=True)
    rating = models.CharField(max_length=32, blank=True, null=True)
    action_adventure = models.BooleanField(default=False)
    musics = models.BooleanField(default=False)
    plat_former = models.BooleanField(default=False)
    puzzles_brain = models.BooleanField(default=False)
    games = models.BooleanField(default=False)
    racing = models.BooleanField(default=False)
    role = models.BooleanField(default=False)
    playing = models.BooleanField(default=False)
    shooter = models.BooleanField(default=False)
    simulation = models.BooleanField(default=False)
    sports = models.BooleanField(default=False)
    strategy = models.BooleanField(default=False)


class BabyItems(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class Toys(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class TicketsVouchers(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    number = models.CharField(max_length=32, blank=True, null=True)


class Books(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    type = models.CharField(max_length=128)


class Music(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    duration = models.CharField(max_length=128)


class FreeStuff(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class DVDsAndMovies(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class FurnitureHomeGarden(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)


class MobilePhonesAndTablets(Classified):
    age = models.CharField(max_length=32, blank=True, null=True)
    usage = models.CharField(max_length=32, blank=True, null=True)
    condition = models.CharField(max_length=32)
    warranty = models.CharField(max_length=32, blank=True, null=True)

    class Meta:
        abstract = True


class Pets(Classified):
    pass


class Collectibles(Classified):
    pass


class LostOrFound(Classified):
    pass


class OtherClassified(Classified):
    pass
