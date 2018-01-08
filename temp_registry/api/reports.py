import datetime

from datetime import date

from dateutil.relativedelta import relativedelta

from temp_registry.models import TemperatureReadout


def dailyReport(start_date, mac):

    def calculate_hourly_average(hourly_readouts):

        hourly_total = 0
        for readout in hourly_readouts:
            hourly_total = hourly_total + readout.temperature

        if not len(hourly_readouts) == 0:

            return hourly_total / len(hourly_readouts)
        else:

            return 0

    readouts = TemperatureReadout.objects.filter(timestamp__gte=start_date,
                                                 timestamp__lte=start_date + datetime.timedelta(days=1),
                                                 temp_sensor=mac
                                                 )
    start_hour = start_date
    hourly_averages = []

    for hour_count in range(1, 25):

        hourly_readouts = readouts.filter(
            timestamp__gte=start_hour,
            timestamp__lte=(start_hour + datetime.timedelta(hours=1))
        )

        hourly_average = calculate_hourly_average(hourly_readouts)
        hourly_averages.append([start_hour.strftime("%H:%M"), hourly_average])

        start_hour = start_hour + datetime.timedelta(hours=1)

    total = 0
    for average in hourly_averages:
        total = total + average[1]
    report = {
        "general_average": total/len(hourly_averages),
        "individual_averages": hourly_averages
    }
    return report


def weeklyReport(start_date, mac):
    readouts = TemperatureReadout.objects.filter(timestamp__gte=start_date,
                                                 timestamp__lte=start_date + datetime.timedelta(days=7),
                                                 temp_sensor=mac
                                                 )
    start_day = start_date
    daily_averages = []

    for day_count in range(1, 8):

        daily_readouts = readouts.filter(
            timestamp__gte=start_day,
            timestamp__lte=(start_day + datetime.timedelta(days=1))
        )

        total = 0
        for readout in daily_readouts:
            total = total + readout.temperature

        daily_averages.append(total/len(daily_readouts))

        start_day = start_day + datetime.timedelta(days=1)

    total = 0
    for average in daily_averages:
        total = total + average
    report = {
        "general_average": total/len(daily_averages),
        "individual_averages": daily_averages
    }
    return report


def monthlyReport(start_date, mac):
    ###################
    # NOT FINISHED
    ###################
    readouts = TemperatureReadout.objects.filter(timestamp__gte=start_date,
                                                 timestamp__lte=start_date + relativedelta(months=+1),
                                                 temp_sensor=mac
                                                 )
    start_day = start_date
    end_day = start_date + relativedelta(months=+1)
    day_delta = (end_day - start_day).days
    daily_averages = []

    for day_count in range(1, day_delta):

        daily_readouts = readouts.filter(
            timestamp__gte=start_day,
            timestamp__lte=(start_day + datetime.timedelta(days=1))
        )

        total = 0
        for readout in daily_readouts:
            total = total + readout.temperature

        daily_averages.append(total/len(daily_readouts))

        start_day = start_day + datetime.timedelta(days=1)

    total = 0
    for average in daily_averages:
        total = total + average
    report = {
        "general_average": total/len(daily_averages),
        "individual_averages": daily_averages
    }
    return report


def yearlyReport(start_date, mac):
    readouts = TemperatureReadout.objects.filter(timestamp__gte=start_date,
                                                 timestamp__lte=add_years(start_date, 1),
                                                 temp_sensor=mac
                                                 )
    start_month = start_date
    monthly_averages = []

    for month_count in range(1, 12):

        month_readouts = readouts.filter(
            timestamp__gte=start_month,
            timestamp__lte=(start_month + relativedelta(month=1))
        )

        total = 0
        for readout in month_readouts:
            total = total + readout.temperature

        monthly_averages.append(total/len(month_readouts))

        start_month = start_month + datetime.timedelta(days=1)

    total = 0
    for average in monthly_averages:
        total = total + average
    report = {
        "general_average": total/len(monthly_averages),
        "individual_averages": monthly_averages
    }
    return report


def add_years(d, years):
    """Return a date that's `years` years after the date (or datetime)
    object `d`. Return the same calendar date (month and day) in the
    destination year, if it exists, otherwise use the following day
    (thus changing February 29 to March 1).

    """
    try:
        return d.replace(year=d.year + years)
    except ValueError:
        return d + (date(d.year + years, 1, 1) - date(d.year, 1, 1))
