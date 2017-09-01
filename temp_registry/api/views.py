import json

from decimal import Decimal

from django.core import serializers
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from temp_registry.forms import BuildingForm, RoomForm
from temp_registry.models import TemperatureSensor, TemperatureReadout, Building, Room
from temp_registry.serializers import ExtJsonSerializer


class TemperatureRegistration(View):

    def get(self, request):
        return JsonResponse(data={}, status=200)

    @csrf_exempt
    def post(self, request):
        #sensor_data = json.loads(request.POST["data"]) #para x-www-form-urlencoded
        sensor_data = json.loads(request.body.decode('utf-8')) #para body (byte string)

        if TemperatureSensor.objects.filter(MAC_address=sensor_data["sensor_id"]).exists():

            temperature = Decimal(sensor_data["temperature"])
            TemperatureReadout(
                temp_sensor=TemperatureSensor.objects.get(MAC_address=sensor_data["sensor_id"]),
                temperature=temperature
            ).save()
            print(temperature)
            print(sensor_data["sensor_id"])

            return JsonResponse(data=sensor_data, status=200)
        else:
            return JsonResponse(data=sensor_data, status=404)


class TemperatureSensorsGetter(View):

    def get(self, request):
        serialized_sensors = ExtJsonSerializer().serialize(
            queryset=TemperatureSensor.objects.all(), props=['last_known_temperature'])
        return HttpResponse(serialized_sensors, content_type="application/json")


class TemperatureReportGetter(View):

    def get(self, request, MAC_address):

        if TemperatureSensor.objects.filter(MAC_address=MAC_address).exists():
            readouts = TemperatureReadout.objects.filter(
                temp_sensor=TemperatureSensor.objects.get(MAC_address=MAC_address))

            readouts.order_by("-timestamp")
            serialized_readouts = serializers.serialize("json", readouts)

            return HttpResponse(serialized_readouts, content_type="application/json")


class SensorDelete(View):

    def get(self, request, MAC_address):
        sensor = TemperatureSensor.objects.get(MAC_address=MAC_address)
        sensor.delete()
        return HttpResponseRedirect("/general/")


class BuildingRegister(View):

    def post(self, request):
        form = BuildingForm(request.POST)

        if form.is_valid() and not Building.objects.filter(name=form.base_fields["name"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/room_building_registration/")

        else:
            return HttpResponseRedirect("/room_building_registration/")


class RoomRegister(View):

    def post(self, request):
        form = RoomForm(request.POST)

        if form.is_valid() and not Room.objects.filter(name=form.base_fields["name"],
                                                       building=form.base_fields["building"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/room_building_registration/")

        else:
            return HttpResponseRedirect("/room_building_registration/")