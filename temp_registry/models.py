from django.core.validators import RegexValidator
from django.db import models

# Create your models here.


class TemperatureSensor(models.Model):
    MAC_address = models.CharField(primary_key=True, max_length=17, validators=[
        RegexValidator(regex=r'^[a-f0-9:]{17}$', message="La dirección mac no tiene un formato válido")])
    building = models.ForeignKey("Building", on_delete=models.SET_NULL, null=True)
    room = models.ForeignKey("Room", on_delete=models.SET_NULL, null=True)
    upper_temp_limit = models.DecimalField(max_digits=5, decimal_places=3)
    lower_temp_limit = models.DecimalField(max_digits=5, decimal_places=3)

    @property
    def last_known_temperature(self):
        readouts = TemperatureReadout.objects.filter(temp_sensor=self)
        if readouts.exists():
            return readouts.latest('timestamp').temperature
        else:
            return "N/A"

    @property
    def building_name(self):
        if self.building:
            return self.building.name
        else:
            return None

    @property
    def room_name(self):
        if self.room:
            return self.room.name
        else:
            return None


class TemperatureReadout(models.Model):
    temp_sensor = models.ForeignKey(TemperatureSensor, models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=3)
    humidity = models.DecimalField(max_digits=5, decimal_places=3)
    timestamp = models.DateTimeField(auto_now=True)


class Building(models.Model):
    name = models.CharField(unique=True, max_length=50)

    @property
    def rooms(self):
        return Room.objects.filter(building=self)

    def __str__(self):
        return self.name


class Room(models.Model):
    name = models.CharField(max_length=50)
    building = models.ForeignKey(Building, models.CASCADE)

    def __str__(self):
        return self.name
