import json

from decimal import Decimal
from django.http.response import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from temp_registry.models import TemperatureSensor, TemperatureReadout
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
