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
            humidity = Decimal(sensor_data["humidity"])
            TemperatureReadout(
                temp_sensor=TemperatureSensor.objects.get(MAC_address=sensor_data["sensor_id"]),
                temperature=temperature,
                humidity=humidity
            ).save()

            return JsonResponse(data=sensor_data, status=200)
        else:
            return JsonResponse(data=sensor_data, status=404)


class TemperatureSensorsGetter(View):

    def get(self, request):
        serialized_sensors = ExtJsonSerializer().serialize(
            queryset=TemperatureSensor.objects.all(),
            props=[
                'last_known_temperature',
                'building_name',
                'room_name'
            ])
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

        if form.is_valid() and not Building.objects.filter(name=form.cleaned_data["name"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/room_building_registration/")

        else:
            return HttpResponseRedirect("/room_building_registration/")


class RoomRegister(View):

    def post(self, request):
        form = RoomForm(request.POST)

        #b = form.cleaned_data["building"]

        if form.is_valid() and not Room.objects.filter(name=form.cleaned_data["name"],
                                                       building=form.cleaned_data["building"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/room_building_registration/")

        else:
            return HttpResponseRedirect("/room_building_registration/")


class BuildingRoomsGetter(View):

    def get(self, request, building):

        if Building.objects.filter(id=building).exists():

            building_rooms = Room.objects.filter(building=Building.objects.get(id=building))
            return HttpResponse(serializers.serialize("json", building_rooms))

        else:
            return HttpResponse("[]", content_type="application/json")


class BuildingEraser(View):

    def post(self, request):
        building_id = request.POST["building"]

        if Building.objects.filter(id=building_id).exists():
            Building.objects.get(id=building_id).delete()

            return HttpResponseRedirect("/room_building_delete/")

class RoomEraser(View):

    def post(self, request):
        room_id = request.POST["room"]

        if Room.objects.filter(id=room_id).exists():
            Room.objects.get(id=room_id).delete()

            return HttpResponseRedirect("/room_building_delete/")