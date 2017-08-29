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
from temp_registry.views import *

urlpatterns = [
    url(r'^register_sensor/', SensorRegistration.as_view(), name="register-sensor"),
    url(r'^general/', GeneralPage.as_view(), name="general"),
    url(r'^update_sensor/mac=([^/]+)', SensorUpdate.as_view(), name="update-sensor"),
    url(r'^', include("temp_registry.api.urls"))
]
