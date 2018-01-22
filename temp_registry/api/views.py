import json
import _thread
import datetime

from decimal import Decimal

from django.core import serializers
from django.http.response import JsonResponse, HttpResponse, HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.base import View

from temp_registry.alerts import send_overheat_alert, send_freezing_alert
from temp_registry.api.reports import daily_report, weekly_report, monthly_report, yearly_report
from temp_registry.forms import BuildingForm, RoomForm
from temp_registry.models import TemperatureSensor, TemperatureReadout, Building, Room, AlertTimeout
from temp_registry.serializers import ExtJsonSerializer


class TemperatureRegistration(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /register_temp/"""
    timeout_duration = 5

    @csrf_exempt
    def post(self, request):
        """Esta función se llama cuando el se hace un POST a la url de /register_temp/. La función
            se encarga de verificar que el mensaje venga de un sensor registrado, luego guarda la
            lectura de temperatura y humedad que contenga el cuerpo del mensaje de POST y por
            último llama a una función para verificar si se han excedido los límites indicados
            para el sensor. """

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
        """Esta función se encarga de decidir si se debe evaluar la lectura del sensor contra
        los límites disctados para un sensor. Si hubo una alerta enviada para el sensor en los
        últimos 5 minutos, no se evaluará la lectura."""

        if not AlertTimeout.objects.filter(temp_sensor=temp_sensor).exists():
            self.evaluate_temperture(temperature, temp_sensor)

        elif datetime.datetime.today() > AlertTimeout.objects.get(temp_sensor=temp_sensor).timeout:
            AlertTimeout.objects.get(temp_sensor=temp_sensor).delete()
            self.evaluate_temperture(temperature, temp_sensor)

    def evaluate_temperture(self, temperature, temp_sensor):
        """Esta función se encarga de evaluar la temperatura leída por un sensor contra su límite
        inferior y superior. Si alguno de estos límites es excedido, se llama a la función que
        envía la alerta por email. También se crea un indicador de alerta en la base de datos para
        evitar que se envíen múltiples emails para la misma alerta."""
        if temperature > temp_sensor.upper_temp_limit:
            AlertTimeout(
                temp_sensor=temp_sensor,
                timeout=(datetime.datetime.today() + datetime.timedelta(minutes=self.timeout_duration))
            ).save()
            _thread.start_new_thread(send_overheat_alert, (temp_sensor, temperature))

        elif temperature < temp_sensor.lower_temp_limit:
            AlertTimeout(
                temp_sensor=temp_sensor,
                timeout=(datetime.datetime.today() + datetime.timedelta(minutes=self.timeout_duration))
            ).save()
            _thread.start_new_thread(send_freezing_alert, (temp_sensor, temperature))


class TemperatureSensorsGetter(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /temperature_sensors/"""

    def get(self, request):
        """Esta función se llama cuando el se hace un GET a la url de /temperature_sensors/. La función
            se encarga de hacer una consulta para encontrar la información de todos los sensores de temperatura
            para luego serializarlos junto con sus propiedades."""

        serialized_sensors = ExtJsonSerializer().serialize(
            queryset=TemperatureSensor.objects.all(),
            props=[
                'last_known_temperature',
                'building_name',
                'room_name'
            ])
        return HttpResponse(serialized_sensors, content_type="application/json")


class TemperatureReportGetter(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /temperature_readouts/mac=<MAC de un sensor>"""

    def get(self, request, MAC_address):
        """Esta función se llama cuando el se hace un GET a la url de /temperature_readouts/mac=<MAC de un sensor>. La función
            se encarga de hacer una consulta de todas las lecturas de temperatura de un sensor indicado. Estas lecturas se
            ordenan de más nueva a más antigua y se serializan."""

        if TemperatureSensor.objects.filter(MAC_address=MAC_address).exists():
            readouts = TemperatureReadout.objects.filter(
                temp_sensor=TemperatureSensor.objects.get(MAC_address=MAC_address))

            readouts.order_by("-timestamp")
            serialized_readouts = serializers.serialize("json", readouts)

            return HttpResponse(serialized_readouts, content_type="application/json")


class SensorDelete(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /delete_sensor/mac=<MAC de un sensor>"""

    def get(self, request, MAC_address):
        """Esta función se llama cuando el se hace un GET a la url de /temperature_readouts/mac=<MAC de un sensor>. La
         función se encarga de eliminar de la base de datos el sensor indicado."""

        sensor = TemperatureSensor.objects.get(MAC_address=MAC_address)
        sensor.delete()
        return HttpResponseRedirect("/general/")


class BuildingRegister(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /register_building/"""

    def post(self, request):
        """Esta función se llama cuando el se hace un POST a la url de /register_building/. La función se encarga de
            verificar que el edificio indicado no ya exista en la base de datos para luego guardar su información en
            la base de datos."""

        form = BuildingForm(request.POST)

        if form.is_valid() and not Building.objects.filter(name=form.cleaned_data["name"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/room_building_registration/")

        else:
            return HttpResponseRedirect("/room_building_registration/")


class RoomRegister(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /register_room/"""

    def post(self, request):
        """Esta función se llama cuando el se hace un POST a la url de /register_room/. La función se encarga de
            verificar que el cuarto indicado no ya exista en la base de datos para luego guardar su información en
            la base de datos."""
        form = RoomForm(request.POST)

        #b = form.cleaned_data["building"]

        if form.is_valid() and not Room.objects.filter(name=form.cleaned_data["name"],
                                                       building=form.cleaned_data["building"]).exists():

            form.save(commit=True)
            return HttpResponseRedirect("/room_building_registration/")

        else:
            return HttpResponseRedirect("/room_building_registration/")


class BuildingRoomsGetter(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /rooms/building=<id de un edificio>"""

    def get(self, request, building):
        """Esta función se llama cuando el se hace un GET a la url de /rooms/building=<id de un edifico>. La función se
         encarga de verificar que exista el edificio indicado para luego obtener todos los cuartos contenidos en ese
         edificio y serializar su información"""

        if Building.objects.filter(id=building).exists():

            building_rooms = Room.objects.filter(building=Building.objects.get(id=building))
            return HttpResponse(serializers.serialize("json", building_rooms), content_type="application/json")

        else:
            return HttpResponse("[]", content_type="application/json")


class BuildingEraser(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /delete_building/"""

    def post(self, request):
        """Esta función se llama cuando el se hace un POST a la url de /delete_building/. La función se encarga de
            verificar que exista el edificio indicado para luego eliminarlo de la base de datos"""
        building_id = request.POST["building"]

        if Building.objects.filter(id=building_id).exists():
            Building.objects.get(id=building_id).delete()

            return HttpResponseRedirect("/room_building_delete/")


class RoomEraser(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /delete_room/"""

    def post(self, request):
        """Esta función se llama cuando el se hace un POST a la url de /delete_room/. La función se encarga de
            verificar que exista el cuarto indicado para luego eliminarlo de la base de datos"""
        room_id = request.POST["room"]

        if Room.objects.filter(id=room_id).exists():
            Room.objects.get(id=room_id).delete()

            return HttpResponseRedirect("/room_building_delete/")


class GeneralTempReporter(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url
        /general_reports/mac=<MAC de un sensor>/startDate=<dia de inicio>/range=<rango del reporte>"""

    def get(self, request, mac, start_date, range):
        """Esta función se llama cuando el se hace un GET a la url de
            /general_reports/mac=<MAC de un sensor>/startDate=<dia de inicio>/range=<rango del reporte>. La función se
            encarga de transformar la fecha en formato yyyy-mm-dd a un objeto de fecha con el que se puedan hacer consultas
            a la base de datos. Después de esto, dependiendo del rango del reporte, llama a la función indicada para
            generar el reporte y por último lo serializa"""

        report = {}
        date = datetime.datetime.strptime(start_date, "%Y-%m-%d")

        if range == "day":
            report = daily_report(date, mac)

        elif range == "week":
            report = weekly_report(date, mac)

        elif range == "month":
            report = monthly_report(date, mac)

        elif range == "year":
            report = yearly_report(date, mac)

        return JsonResponse(report)
