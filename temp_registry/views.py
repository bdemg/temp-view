import json

from decimal import Decimal
from django.http import HttpResponse
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from temp_registry.forms import SensorForm, RoomForm, BuildingForm
from temp_registry.models import TemperatureSensor, TemperatureReadout, Room, Building


class SensorRegistration(View):
    template_name = "temp_registry/sensor_registration.html"
    existing_error = "Ya existe un sensor con esa dirección MAC"

    def get(self, request):
        context = {"form": SensorForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        form = SensorForm(request.POST)

        if form.is_valid() and not TemperatureSensor.objects.filter(
                MAC_address=form.cleaned_data["MAC_address"]).exists():

            TemperatureSensor(
                MAC_address=form.cleaned_data["MAC_address"],
                building=form.cleaned_data["building"],
                room=Room.objects.get(id=int(request.POST["room"])),
                upper_temp_limit=form.cleaned_data["upper_temp_limit"],
                lower_temp_limit=form.cleaned_data["lower_temp_limit"]
            ).save()

            return HttpResponseRedirect("/general/")
        else:

            return render(request, self.template_name, {"form": form, "existing_error": self.existing_error})


class SensorUpdate(View):
    template_name = "temp_registry/sensor_update.html"

    def get_id_or_empty_string(self, value):
        if value:
            return value.id
        else:
            ""

    def get(self, request, MAC_address):

        if TemperatureSensor.objects.filter(MAC_address=MAC_address).exists():

            sensor = TemperatureSensor.objects.get(MAC_address=MAC_address)
            context = {
                "form": SensorForm(instance=sensor),
                "MAC_address": MAC_address,
                "selected_room": self.get_id_or_empty_string(sensor.room)
            }
        else:
            context = {"error": "No se encuentra el sensor especificado"}

        return render(request, self.template_name, context)

    def post(self, request, MAC_address):

        instance = get_object_or_404(TemperatureSensor, MAC_address=MAC_address)
        form = SensorForm(request.POST or None, instance=instance)

        if form.is_valid():

            TemperatureSensor(
                MAC_address=form.cleaned_data["MAC_address"],
                building=form.cleaned_data["building"],
                room=Room.objects.get(id=int(request.POST["room"])),
                upper_temp_limit=form.cleaned_data["upper_temp_limit"],
                lower_temp_limit=form.cleaned_data["lower_temp_limit"]
            ).save()
            return HttpResponseRedirect("/general/")
        else:
            return render(request, self.template_name, {"form": form, "MAC_address": MAC_address})


class GeneralPage(View):
    template_name = "temp_registry/general_view.html"

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)


class RoomAndBuildingRegistrationPage(View):
    template_name = "temp_registry/building_and_room_registry.html"

    def get(self, request):
        context = {"room_form": RoomForm(), "building_form": BuildingForm()}
        return render(request, self.template_name, context)


class RoomAndBuildingDeletePage(View):
    template_name = "temp_registry/building_and_room_delete.html"

    def get(self, request):
        context = {"rooms": Room.objects.all(), "buildings": Building.objects.all()}
        return render(request, self.template_name, context)


class ReportsPage(View):
    template_name = "temp_registry/reports.html"

    def get(self, request):
        context = {"sensors": TemperatureSensor.objects.all()}
        return render(request, self.template_name, context)