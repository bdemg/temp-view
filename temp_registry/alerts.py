from celery.app import shared_task
from django.core.mail.message import EmailMultiAlternatives

from temp_registry.models import AlertEmails


def send_overheat_alert(sensor, temperature_reading):
    """Esta función contruye el mensaje de sobrecalentamiento que se manda cuando la
    temperatura registrada por un sensor sobrepasa su límite superior"""

    mail_subject = 'El sensor de la sala {0} ha reportado temperatura abnormal'.format(sensor.room.name)

    overheat_message = """<p> El sensor con la dirección MAC {0} que se encuentra en el salón {1} del edificio {2} 
        ha reportado una temperaura de {3}°, que se encuentra por encima de su límite de {4}°"""

    mail_content = overheat_message.format(
        sensor.MAC_address,
        sensor.room.name,
        sensor.building.name,
        temperature_reading,
        sensor.upper_temp_limit
    )
    send_email_async(subject=mail_subject, content=mail_content)


def send_freezing_alert(sensor, temperature_reading):
    """Esta función contruye el mensaje de sobreenfriamiento que se manda cuando la
    temperatura registrada por un sensor sobrepasa su límite inferior"""

    mail_subject = 'El sensor de la sala {0} ha reportado temperatura abnormal'.format(sensor.room.name)

    underheat_message = """<p> El sensor con la dirección MAC {0} que se encuentra en el salón {1} del edificio {2} 
        ha reportado una temperaura de {3}°, que se encuentra por debajo de su límite de {4}°"""

    mail_content = underheat_message.format(
        sensor.MAC_address,
        sensor.room.name,
        sensor.building.name,
        temperature_reading,
        sensor.lower_temp_limit
    )
    send_email_async(subject=mail_subject, content=mail_content)


@shared_task
def send_email_async(subject, content, to="alertas_sensor@uady.edu.mx", content_type="text/html"):
    """Función que envía un email con el contenido que se le designe."""

    try:
        msg = EmailMultiAlternatives(subject=subject, body=content, from_email="sensorbot@uady.edu.mx",
                                     to=[to])
        if content_type == "text/html":
            msg.attach_alternative(content, "text/html")
        msg.send()
    except:
        print("ERROR SENDING EMAILS")
