from django import forms

from .models.motor_model import Motors, Car, MotorCycle, AutoAccessoriesAndParts, HeavyVehicles


class CarForm(forms.ModelForm):

    class Meta:
        model = Car
        fields = '__all__'
