"""temp_service URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.11/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from django.contrib import admin
from django.conf.urls import include
from temp_registry.api.views import *

urlpatterns = [
    url(r'^register_temp/', TemperatureRegistration.as_view()),
    url(r'^temperature_sensors/', TemperatureSensorsGetter.as_view()),
    url(r'^temperature_readouts/mac=([^/]+)', TemperatureReportGetter.as_view()),
    url(r'^delete_sensor/mac=([^/]+)', SensorDelete.as_view(), name="delete-sensor"),
]