from django.core.validators import RegexValidator
from django.db import models

# Create your models here.


class TemperatureSensor(models.Model):
    MAC_address = models.CharField(primary_key=True, max_length=17, validators=[
        RegexValidator(regex=r'^[a-f0-9:]{17}$', message="La dirección mac no tiene un formato válido")])
    building = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    upper_temp_limit = models.DecimalField(max_digits=5, decimal_places=3)
    lower_temp_limit = models.DecimalField(max_digits=5, decimal_places=3)

    @property
    def last_known_temprerature(self):
        return TemperatureReadout.objects.filter(temp_sensor=self).order_by('-timestamp').latest()


class TemperatureReadout(models.Model):
    temp_sensor = models.ForeignKey(TemperatureSensor, models.CASCADE)
    temperature = models.DecimalField(max_digits=5, decimal_places=3)
    timestamp = models.DateTimeField(auto_now=True)
