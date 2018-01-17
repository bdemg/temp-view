from django.core.validators import RegexValidator
from django.db import models

# Create your models here.


class TemperatureSensor(models.Model):
    """Clase modelo para guardar y acceder a la información de los sensores."""
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
            return "N/A"

    @property
    def room_name(self):
        if self.room:
            return self.room.name
        else:
            return "N/A"


class TemperatureReadout(models.Model):
    """Clase modelo para guardar y acceder a las lecturas de temperatura de un sensor"""
    temp_sensor = models.ForeignKey(TemperatureSensor, models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=3)
    humidity = models.DecimalField(max_digits=5, decimal_places=3)
    timestamp = models.DateTimeField(auto_now=True)


class Building(models.Model):
    """Clase modelo para guardar y acceder a la información de un edificio"""
    name = models.CharField(unique=True, max_length=50)

    @property
    def rooms(self):
        return Room.objects.filter(building=self)

    def __str__(self):
        return self.name


class Room(models.Model):
    """Clase modelo para guardar y acceder a la información de un cuarto"""
    name = models.CharField(max_length=50)
    building = models.ForeignKey(Building, models.CASCADE)

    def __str__(self):
        return self.name


class AlertEmails(models.Model):
    """Clase modelo para guardar y acceder a los emails a los que se
    mandan correos de alerta si se ha excedido el límite de temperatura
    de un sensor"""
    email = models.EmailField(max_length=254, unique=True)


class AlertTimeout(models.Model):
    """Clase modelo para guardar y acceder a los tempoizadores que evitan que
    las alertas por email se manden por una cantidad de tiempo"""
    temp_sensor = models.ForeignKey(TemperatureSensor, models.CASCADE)
    timeout = models.DateTimeField()
