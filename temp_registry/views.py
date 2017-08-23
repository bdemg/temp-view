import json

from decimal import Decimal
from django.http import HttpResponse
from django.http.response import JsonResponse, HttpResponseRedirect
from django.shortcuts import render

# Create your views here.
from django.views import View
from django.views.decorators.csrf import csrf_exempt

from temp_registry.forms import SensorForm
from temp_registry.models import TemperatureSensor, TemperatureReadout


class TemperatureRegistration(View):

    def get(self, request):
        return JsonResponse(data={}, status=200)

    @csrf_exempt
    def post(self, request):
        sensor_data = json.loads(request.POST["data"]) #para x-www-form-urlencoded
        #sensor_data = json.loads(request.body.decode('utf-8')) #para body (byte string)

        if TemperatureSensor.objects.filter(id=sensor_data["sensor_id"]).exists():

            temperature = Decimal(sensor_data["temperature"])
            TemperatureReadout(
                temp_sensor=sensor_data["sensor_id"],
                temperature=temperature
            ).save()
            print(temperature)
            print(sensor_data["sensor_id"])

            return JsonResponse(data=sensor_data, status=200)
        else:
            return JsonResponse(data=sensor_data, status=404)


class SensorRegistration(View):
    template_name = "temp_registry/sensor_registration.html"
    existing_error = "Ya existe un sensor con esa dirección MAC"

    def get(self, request):
        context = {"form": SensorForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        form = SensorForm(request.POST)

        if form.is_valid() and not TemperatureSensor.objects.filter(MAC_address=form.base_fields["MAC_address"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/general/")
        else:

            return render(request, self.template_name, {"form": form, "existing_error": self.existing_error})


class GeneralPage(View):
    template_name = "temp_registry/general_view.html"

    def get(self, request):
        context = {}
        return render(request, self.template_name, context)