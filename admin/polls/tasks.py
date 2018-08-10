from django.http import HttpResponse


from django.template import loader
from django.contrib.auth import models
import socket
import json
from pprint import pprint
import requests
from .models import Measurements, MeasureData, History,BackgroundTaskModel,MeasureDataView,Concentrations,AQINowCastHistory
import time
from datetime import datetime,timedelta
from django.conf import settings
from background_task import background
from django.db.models import Sum
from django.db import transaction
from django.contrib import messages
import logging
from .tools import initDeviceConnection,getDeviceStatus,getDeviceMeasure,deviceDatetime,query_12_set_concentrations,nowcast,air_quality_index

logger = logging.getLogger(__name__)





@background()
def stop():
    with transaction.atomic():
        BackgroundTaskModel.objects.all().delete();



@background()
def notify_user(measurement_id):



    # EL RAW DATA TIENE DOS VARIANTES UNA CON CAMPOS CALCULADOS Y OTRA CON CONSULTANDO LA HORA REGISTRADA, SI BIEN AMBOS CASOS  SE TENDRA EL ELAPSED
    s = initDeviceConnection()

    if s is not None:
        status = getDeviceStatus(s)

        if 'Running' in status :


            device_elapsed_time,device_data,error,alarm =  getDeviceMeasure(s)
            current_measure = Measurements.objects.get(id=measurement_id)
            lastest_measuredata_number =  MeasureDataView.objects.filter(measurements = measurement_id).count()

            measure_data_save = True
            # VERIFICA QUE NO SEA EL PRIMER ELEMENTO Y QUE NO SEA REPETIDO
            if lastest_measuredata_number != 0:
                lastest_measuredata =  MeasureDataView.objects.filter(measurements = measurement_id).latest('utimestamp')
                if int(lastest_measuredata.elapsed_time) == int(device_elapsed_time):
                    measure_data_save = False
            # VERIFICA QUE EL DATO NO TENGA VALOR CERO
            if device_data == 0:
                measure_data_save = False
            # PERMITE GUARDAR EL ELEMENTO
            if measure_data_save:
                with transaction.atomic():
                     mData = MeasureData(   elapsed_time=device_elapsed_time,  data=device_data,    measurements=current_measure, error=error, alarm=alarm)
                     mData.save()
        else:
            stop()
            return



        # PROMEDIO HORARIO - Concentraciones


        inicio_real = deviceDatetime(s)

        inicio = inicio_real - timedelta(minutes=inicio_real.minute) - timedelta(seconds=inicio_real.second)
        final =  inicio + timedelta(hours=1)

        cantidad = MeasureDataView.objects.all().filter(utimestamp__range=[inicio,final]).count()
        total = MeasureDataView.objects.all().filter(utimestamp__range=[inicio,final]).aggregate(Sum('data'))['data__sum']




        with transaction.atomic():
            current_range = Concentrations.objects.all().filter(start=inicio,final=final)

            if current_range.count() > 0:
                current_concentration = current_range.first()
                current_concentration.sum=total
                current_concentration.count=cantidad
                current_concentration.save()
            else:
                c = Concentrations(real_start=inicio_real, start=inicio, final=final, sum=total, count=cantidad)
                c.save()


        # Indice de calidad del aire por hora

        c = query_12_set_concentrations(inicio_real)

        average = nowcast(c)
        value, message, color = air_quality_index(average)

        last_concentration_hour = inicio_real - timedelta(minutes=inicio_real.minute) - timedelta(seconds=inicio_real.second)
        with transaction.atomic():
            stored = AQINowCastHistory.objects.all().filter(timestamp=last_concentration_hour)
            if stored.count() == 0:
                AQINowCastHistory(timestamp=last_concentration_hour,data=value).save()

        ''' Finalizar el socket '''

        s.close()
    else:
        stop()
        return
        # messages.add_message(request,messages.ERROR, 'No se puede detener el dispositivo. ')
