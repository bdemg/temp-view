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
    """Clase vista que se encarga de manejar las peticiones hechas a la url /register_sensor/"""

    template_name = "temp_registry/sensor_registration.html"
    existing_error = "Ya existe un sensor con esa dirección MAC"

    def get(self, request):
        """Esta función se llama cuando el se hace un GET a la url de /register_sensor/. La función
         se encarga de desplegar la página donde se puede hacer el registro de los sensores por
         medio de un formulario."""

        context = {"form": SensorForm()}
        return render(request, self.template_name, context)

    def post(self, request):
        """Esta función se llama cuando el se hace un POST a la url de /register_sensor/. La función
            se encarga de leer los datos ingresados en el formulario de registro de sensor y, si no
            se tiene uno registrado con la misma MAC, se guarda la información en la base de datos."""

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
    """Clase vista que se encarga de manejar las peticiones hechas a la url /update_sensor/mac=<MAC_del_sensor>/"""

    template_name = "temp_registry/sensor_update.html"

    def get_id_or_empty_string(self, value):
        if value:
            return value.id
        else:
            ""

    def get(self, request, MAC_address):
        """Esta función se llama cuando el se hace un GET a la url de /update_sensor/mac=<MAC_del_sensor>/.
            La función se encarga de obtener los datos del sensor indicado y desplegar la página donde
            se puede modificar los datos relativos a este por medio de un formulario."""

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
        """Esta función se llama cuando el se hace un POST a la url de /update_sensor/mac=<MAC_del_sensor>/.
            La función se encarga de verificar si existe el sensor correspondiente a la MAC recibida para
            luego actualizar los datos de este con la información recibida por medio del formulario de
            actualización."""

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
    """Clase vista que se encarga de manejar las peticiones hechas a la url /general/"""

    template_name = "temp_registry/general_view.html"

    def get(self, request):
        """Esta función se llama cuando el se hace un GET a la url de /general/.
            La función se encarga de desplegar la pagina inicial del sitio web."""

        context = {}
        return render(request, self.template_name, context)


class RoomAndBuildingRegistrationPage(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /room_building_registration/"""

    template_name = "temp_registry/building_and_room_registry.html"

    def get(self, request):
        """Esta función se llama cuando el se hace un GET a la url de /room_building_registration/.
            La función se encarga de desplegar la pagina donde se pueden registrar nuevos cuartos
            y edificios."""

        context = {"room_form": RoomForm(), "building_form": BuildingForm()}
        return render(request, self.template_name, context)


class RoomAndBuildingDeletePage(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /room_building_delete/"""

    template_name = "temp_registry/building_and_room_delete.html"

    def get(self, request):
        """Esta función se llama cuando el se hace un GET a la url de /room_building_delete/.
            La función se encarga de desplegar la pagina donde se puede elegir un cuarto o
            edificio para eliminar."""

        context = {"rooms": Room.objects.all(), "buildings": Building.objects.all()}
        return render(request, self.template_name, context)


class ReportsPage(View):
    """Clase vista que se encarga de manejar las peticiones hechas a la url /reports/"""

    template_name = "temp_registry/general_reports.html"

    def get(self, request):
        """Esta función se llama cuando el se hace un GET a la url de /reports/. La función se encarga
            de desplegar la pagina donde se puede ingresar el sensor, período y fecha para generar un
            reporte con las lecturas del sensor."""

        context = {"sensors": TemperatureSensor.objects.all()}
        return render(request, self.template_name, context)