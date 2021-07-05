from django.contrib import admin
from .models.motor_model import Car, MotorCycle, AutoAccessoriesAndParts, HeavyVehicles

admin.site.register(Car)
admin.site.register(MotorCycle)
admin.site.register(AutoAccessoriesAndParts)
admin.site.register(HeavyVehicles)
