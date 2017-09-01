from django import forms
from temp_registry.models import TemperatureSensor, Building, Room


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
        help_texts = {
            'MAC_address': 'La dirección debe estar en el formato ee:ee:ee:ee:ee:ee',
        }


class BuildingForm(forms.ModelForm):
    class Meta():
        model = Building
        fields = '__all__'
        labels = {
            "name": "Nombre del edificio",
        }


class RoomForm(forms.ModelForm):
    class Meta():
        model = Room
        fields = "__all__"
        labels = {
            "name": "Nombre del salón",
            "building": "Edificio"
        }