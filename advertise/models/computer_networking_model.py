from django.db import models

from advertise.models.classified_model import ComputersAndNetworking


class Computers(ComputersAndNetworking):
    memory = models.CharField(max_length=32)
    processor_speed = models.CharField(max_length=32)
    hard_drive = models.CharField(max_length=32)


class ComputerComponents(ComputersAndNetworking):
    pass


class NetworkingAndCommunication(ComputersAndNetworking):
    pass


class Software(ComputersAndNetworking):
    pass


class MonitorsPrintersAndOtherPeripherals(ComputersAndNetworking):
    pass


class OtherAccessories(ComputersAndNetworking):
    pass
