from django.db import models


class ElectronicsChoice(models.TextChoices):
    HOME_AUDIO_AND_TURNTABLES = 'Home Audio & Turntables'
    TELEVISIONS = 'Televisions'
    DVD_AND_HOME_THEATER = 'DVD & Home Theater'
    ELECTRONIC_ACCESSORIES = 'Electronic Accessories'
    GADGETS = 'Gadgets'
    CAR_ELECTRONICS = 'Car Electronics'
    MP3_PLAYERS_AND_PORTABLE_AUDIO = 'Mp3 Players and Portable Audio'
    SATELLITE_AND_CABLE_TV = 'Satellite & Cable TV'
    HEALTH_ELECTRONICS = 'Health Electronics'
    SMART_HOME = 'Smart Home'
    WEARABLE_TECHNOLOGY = 'Wearable Technology'
    OTHER = 'Other'


