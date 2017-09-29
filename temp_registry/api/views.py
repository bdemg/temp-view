import json
import _thread
import datetime

from decimal import Decimal

from django.core import serializers
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from temp_registry.alerts import send_overheat_alert, send_freezing_alert
from temp_registry.api.reports import dailyReport, weeklyReport, monthlyReport, yearlyReport
from temp_registry.forms import BuildingForm, RoomForm
from temp_registry.models import TemperatureSensor, TemperatureReadout, Building, Room, AlertTimeout
from temp_registry.serializers import ExtJsonSerializer


class TemperatureRegistration(View):
    timeout_duration = 5

    @csrf_exempt
    def post(self, request):
        #sensor_data = json.loads(request.POST["data"]) #para x-www-form-urlencoded
        sensor_data = json.loads(request.body.decode('utf-8')) #para body (byte string)

        if TemperatureSensor.objects.filter(MAC_address=sensor_data["sensor_id"]).exists():

            temp_sensor = TemperatureSensor.objects.get(MAC_address=sensor_data["sensor_id"])
            temperature = Decimal(sensor_data["temperature"])
            humidity = Decimal(sensor_data["humidity"])
            TemperatureReadout(
                temp_sensor=temp_sensor,
                temperature=temperature,
                humidity=humidity
            ).save()

            self.manage_alert_sending(temperature, temp_sensor)

            return JsonResponse(data=sensor_data, status=200)
        else:
            return JsonResponse(data=sensor_data, status=404)

    def manage_alert_sending(self, temperature, temp_sensor):

        if not AlertTimeout.objects.filter(temp_sensor=temp_sensor).exists():
            self.evaluate_temperture(temperature, temp_sensor)

        elif datetime.datetime.today() > AlertTimeout.objects.get(temp_sensor=temp_sensor).timeout:
            AlertTimeout.objects.get(temp_sensor=temp_sensor).delete()
            self.evaluate_temperture(temperature, temp_sensor)

    def evaluate_temperture(self, temperature, temp_sensor):

        if temperature > temp_sensor.upper_temp_limit:
            AlertTimeout(
                temp_sensor=temp_sensor,
                timeout= (datetime.datetime.today() + datetime.timedelta(minutes=self.timeout_duration))
            ).save()
            _thread.start_new_thread(send_overheat_alert, (temp_sensor, temperature))

        elif temperature < temp_sensor.lower_temp_limit:
            AlertTimeout(
                temp_sensor=temp_sensor,
                timeout=(datetime.datetime.today() + datetime.timedelta(minutes=self.timeout_duration))
            ).save()
            _thread.start_new_thread(send_freezing_alert, (temp_sensor, temperature))


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


class GeneralTempReporter(View):

    def get(self, request, mac, startDate, range):

        report = {}
        date = datetime.datetime.strptime(startDate, "%Y-%m-%d")

        if range == "day":
            report = dailyReport(date, mac)

        elif range == "week":
            report = weeklyReport(date, mac)

        elif range == "month":
            report = monthlyReport(date, mac)

        elif range == "year":
            report = yearlyReport(date, mac)

        return JsonResponse(report)
