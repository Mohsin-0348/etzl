from django.db import models


class GenderChoices(models.TextChoices):
    Female = 'female'
    Male = 'male'


class SocialAccountTypeChoices(models.TextChoices):
    FACEBOOK = 'facebook'
    LINKEDIN = 'linkedin'
    GOOGLE = 'google'
    APPLE = 'apple'


class DeviceTypeChoices(models.TextChoices):
    IOS = "ios"
    ANDROID = "android"
    WEB = "web"


class WeekdayChoices(models.TextChoices):
    MON = "Mon"
    TUE = "Tue"
    WED = "Wed"
    THU = "Thu"
    FRI = "Fri"
    SAT = "Sat"
    SUN = "Sun"


class CurrentCityChoices(models.TextChoices):
    Abu_Dhabi = "Abu Dhabi"
    Al_Ain = "Al Ain"
    Ajman = "Ajman"
    Dubai = "Dubai"
    Fujairah = "Fujairah"
    Sharjah = "Sharjah"
    Umm_Al_Quwain = "Umm Al Quwain"
    Ras_Al_Khaimah = "Ras Al Khaimah"

