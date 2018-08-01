from django.http import HttpResponse


from django.template import loader
from django.contrib.auth import models
import socket
import json
from pprint import pprint
import requests
from polls.models import Measurements, MeasureData, History,BackgroundTaskModel,MeasureDataView,Concentrations,AQINowCastHistory
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
def notify_user(measurement_id):




    s = initDeviceConnection()



    status = getDeviceStatus(s)

    if "Running" in status :


        ''' enviar la peticion, recibir respuesta, guardar en la base de datos '''
        device_elapsed_time,device_data,error,alarm =  getDeviceMeasure(s)



        current_measure = Measurements.objects.get(id=measurement_id)
        '''TODO verificar que no se repita la medicion segun el elapsed_time
            consultar cuales el ultimo MlaeasureData, extraer su elapsed_time y comprobar que no sea repita+
            en caso que no sea repetido se puede guardar '''
        lastest_measuredata_number =  MeasureDataView.objects.filter(measurements = measurement_id).count()
        if lastest_measuredata_number == 0:
            with transaction.atomic():
                mData = MeasureData(   elapsed_time=device_elapsed_time,  data=device_data,    measurements=current_measure, error=error, alarm=alarm)
                mData.save()
        else:
            lastest_measuredata =  MeasureDataView.objects.filter(measurements = measurement_id).latest('utimestamp')
            if int(lastest_measuredata.elapsed_time) != int(device_elapsed_time):
                print("erer")
                with transaction.atomic():
                    mData = MeasureData(   elapsed_time=device_elapsed_time,  data=device_data,    measurements=current_measure)
                    mData.save()
    else:
        '''Se detiene la tarea '''
        with transaction.atomic():
            BackgroundTaskModel.objects.all().delete();
            history = History(author=models.User.objects.get(id=1),action="Grabacion detenida automaticamente",datetime=datetime.now())
            history.save()




    inicio_real = deviceDatetime(s)

    inicio = inicio_real - timedelta(minutes=inicio_real.minute) - timedelta(seconds=inicio_real.second)
    final =  inicio + timedelta(hours=1)
    """ restar 1 al segundo para marcar bien los rangos horarios  """
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
