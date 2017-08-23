from django import forms
from temp_registry.models import TemperatureSensor


class SensorForm(forms.ModelForm):

    class Meta():
        model = TemperatureSensor
        fields = '__all__'
        labels = {
            "MAC_address": "Dirección MAC",
            "building": "Edificio",
            "room": "Salón",
            "upper_temp_limit": "Límite de temperatura superior",
            "lower_temp_limit": "Límite de temperatura inferior",
        }
