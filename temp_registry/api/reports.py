import datetime

from temp_registry.models import TemperatureReadout


def dailyReport(start_date, mac):

    readouts = TemperatureReadout.objects.filter(timestamp__gte=start_date,
                                                 timestamp__lte=start_date + datetime.timedelta(days=1)
                                                 )
    hour_start = start_date
    hourly_averages = []

    for hour_advance in range(1, 25):

        hourly_readouts = readouts.filter(
            timestamp_gte=hour_start,
            timestamp=(hour_start + datetime.timedelta(hours=hour_advance))
        )

        total = 0
        for readout in hourly_readouts:
            total = total + readout.temperature

        hourly_averages.append(total/len(hourly_readouts))

        hour_start = hour_start + datetime.timedelta(hours=hour_advance)

    total = 0
    for average in hourly_averages:
        total = total + average
    report = {
        "total_average": total/len(hourly_averages),
        "hourly_averages": hourly_averages
    }
    return report


def weeklyReport(start_date, mac):
    pass

def monthlyReport(start_date, mac):
    pass

def yearlyReport(start_date, mac):
    pass