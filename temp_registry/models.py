from django.db import models

# Create your models here.


class TemperatureSensor(models.Model):
    MAC_address = models.CharField(primary_key=True, max_length=17)
    building = models.CharField(max_length=50)
    room = models.CharField(max_length=50)
    upper_temp_limit = models.DecimalField(max_digits=5, decimal_places=3)
    lower_temp_limit = models.DecimalField(max_digits=5, decimal_places=3)

    @property
    def last_known_temprerature(self):
        return TemperatureReadout.objects.filter(temp_sensor=self).order_by('-timestamp').latest()


class TemperatureReadout(models.Model):
    temp_sensor = models.ForeignKey(TemperatureSensor)
    temperature = models.DecimalField(max_digits=5, decimal_places=3)
    timestamp = models.DateTimeField(auto_now=True)
