from django.http import HttpResponse


from django.template import loader
from django.contrib.auth import models
import socket
import json
from pprint import pprint
import requests
from polls.models import Measurements, MeasureData, History,BackgroundTaskModel,MeasureDataView,Concentrations,AQIRange
import time
from django.conf import settings
from background_task import background
from datetime import datetime,timedelta
from django.shortcuts import redirect
from django.contrib import messages
from django.db.models import Avg,Max,Min,Sum
from .tools import deviceDatetime,initDeviceConnection

from .tasks import notify_user





def stop_record(request):

    BackgroundTaskModel.objects.all().delete();
    # history = History(author=models.User.objects.get(id=1),action="Grabación terminada",datetime=datetime.now())
    # history.save()
    return redirect('polls.index');









def start_record(request):

    HOST = '172.16.5.2'    # The remote host
    PORT = 3602              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))


    s.send('RSDATETIME\r'.encode())
    datetime = s.recv(1024)
    info = datetime.decode('UTF-8')
    start_date = time.strptime(info,"\r\n%m/%d/%Y,%H:%M:%S\r\n")



    str_history_datetime =  time.strftime("%Y-%m-%d %H:%M:%S",start_date)


    s.send('RMLOGGEDMEAS\r'.encode())
    data = s.recv(1024)
    info =data.decode('UTF-8').split(",")

    device_elapsed_time = info[0].rstrip()
    device_data = info[1].rstrip()


    measure = Measurements(
    author=models.User.objects.get(id=1) ,
    start_timestamp=str_history_datetime,
    current_timestamp=device_elapsed_time)
    measure.save()


    task_created = BackgroundTaskModel.objects.count()
    if not task_created:
        notify_user(measure.id,repeat=10)
    else:
        messages.add_message(request,messages.ERROR, 'Existe un proceso de grabación actualmente. ')



    history = History(author=models.User.objects.get(id=1),action="Grabación iniciada",datetime=str_history_datetime)
    history.save()




    return redirect("polls.index");











def index(request):

    template = loader.get_template('polls/index.html')


    HOST = '172.16.5.2'    # The remote host
    PORT = 3602              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    s.send('MSTATUS\r'.encode())
    status = s.recv(1024)

    s.send('RSDATETIME\r'.encode())
    bdatetime = s.recv(1024)
    datetime = bdatetime.decode('UTF-8')
    list_datetime =  datetime.split(',');



    s.send('RDMN\r'.encode())
    model = s.recv(1024)



    s.send('RDSN\r'.encode())
    serial = s.recv(1024)



    s.send('RMMESSAGES\r'.encode())
    faultb = s.recv(1024)
    fault = faultb.decode('UTF-8')
    array_fault = fault.split(',')

    s.close()






    """resp =  requests.get(url='http://172.16.5.1/temp_y_hum.ssi')
    data =
    data['fecha_y_hora']
    data['temperatura']
    data['humedad']
    data['error']
    """


    context = {
        'device_status': status.decode('UTF-8'),
        'device_date' : list_datetime[0],
        'device_time' : list_datetime[1],
        'device_model' : model.decode('UTF-8'),
        'device_serial' : serial.decode('UTF-8'),
        'device_available_mem' :array_fault[11],
        'history_list' : History.objects.order_by('-datetime')[:8],
        'measuredata_list' : MeasureData.objects.all(),
        'operative_task' : BackgroundTaskModel.objects.all()

    }
    return HttpResponse(template.render(context, request))

def measuredata(request):
    template = loader.get_template('polls/list_measuredata.html')
    context = {

            'measuredata_list' : MeasureDataView.objects.raw("select * from fullmeasure")
    }

    return HttpResponse(template.render(context, request))


def calculate_concentrations(request):

    s = initDeviceConnection()

    # traer la hora del aparato
    current_time = deviceDatetime(s)


    # pedir la hora anterior entera
    last_concentration_hour = current_time - timedelta(minutes=current_time.minute) - timedelta(seconds=current_time.second) - timedelta(hours=1)

    #calcular la hora final del rango
    back_12_hour =  last_concentration_hour - timedelta(hours=12)

    set_12_hours = Concentrations.objects.all().filter(start__lte=last_concentration_hour,final__gte=back_12_hour)[:12]

    c=[]
    c_min = 0
    c_max = 0
    weight_prima = 0
    weight = 0
    y = 0
    aqi = 0
    message = "No concentrations found"
    if set_12_hours.exists():
        for c_hour in set_12_hours:
            c.append(c_hour.data*1000*0.38)




    # NowCast
    #params :
    # -list of 12 concentrations class
    # Range for the index



        c_max = max(c)
        c_min = min(c)
        weight_prima = c_min/c_max
        if weight_prima > 0.5:
            weight = weight_prima
        else:
            weight = 0.5
        i=1
        sum_inf=0
        sum_sup=0
        for x in c:
            sum_sup += pow(weight,i-1)*x
            sum_inf += pow(weight,i-1)
            i=i+1
        y = sum_sup/sum_inf
        range = AQIRange.objects.all();
        for category in range:
            if y >= category.clow and y <= category.chigh :
                clow  = category.clow
                chigh = category.chigh
                ihigh = category.ihigh
                ilow = category.ilow
                message =  category.category



        aqi =  ((y-clow)/(chigh-clow))*(ihigh-ilow) + ilow
    else:
        pass


    template = loader.get_template('polls/nowcastwithconcentrations.html')
    context = {

            'c_raw_set' : set_12_hours,
            # 'c_tags' : cTags,
            'c_set' :c,
            'c_max' :c_max,
            'c_min' :c_min,
            'w_p' : weight_prima,
            'w' :weight,
            'nowcast' : y,
            'nowcast_message' : message,
            'aqi' : aqi
    }

    return HttpResponse(template.render(context, request))





def calculate(request):


    """si no existe datos, mostrar error"""
    inicio = MeasureDataView.objects.latest('utimestamp').utimestamp
    final = inicio - timedelta(hours=1) -timedelta(minutes=1)


    '''Agregar hallar el maximo y el minimo de las doce horas '''
    minmax_inicio= inicio
    minmax_final =  inicio - timedelta(hours=12)

    c_max = MeasureDataView.objects.all().filter(utimestamp__range=[final,inicio]).aggregate(Max('data'))['data__max']
    c_min = MeasureDataView.objects.all().filter(utimestamp__range=[final,inicio]).aggregate(Min('data'))['data__min']


    weight_prima = c_min/c_max

    if weight_prima > 0.5:
        weight = weight_prima
    else:
        weight = 0.5

    cList = []
    ci = []
    cTags = []
    for i in range(12):
        cTags.append(inicio)
        cTags.append(final)
        cList.append(MeasureDataView.objects.all().filter(utimestamp__range=[final,inicio]))
        ci.append( MeasureDataView.objects.all().filter(utimestamp__range=[final,inicio]).aggregate(Avg('data'))['data__avg'])
        inicio = final
        final = inicio - timedelta(hours=1) -timedelta(minutes=1)

    c = []
    for i in ci:
        if i is None :
            c.append(0)
        else:
            c.append(i*1000*0.38)


    i=1
    sum_inf=0
    sum_sup=0

    for x in c:
        sum_sup += pow(weight,i-1)*x
        sum_inf += pow(weight,i-1)
        i=i+1

    y = sum_sup/sum_inf



    if  y>=0.0 and y<=12.0 :
        clow=0
        chigh=12.0
        ilow=0
        ihigh=50
        message= 'Good'
    elif  y>=12.1 and y<=35.4 :
        clow=12.1
        chigh=35.4
        ilow=51
        ihigh=100
        message= 'Moderate'
    elif  y>=35.5 and y<=55.4 :
        clow=35.5
        chigh=55.4
        ilow=101
        ihigh=150
        message = 'Unhealthy for Sensitive Groups'
    elif y>=55.5 and y<=150.4 :
        clow=55.5
        chigh=150.4
        ilow=151
        ihigh=200
        message = 'Unhealthy'
    elif  y>=0.0 and y<=12.0 :
        clow=150.5
        chigh=250.4
        ilow=201
        ihigh=300
        message = 'Very Unhealthy'
    elif  y>=250.5 and y<=350.4 :
        clow=250.5
        chigh=350.4
        ilow=301
        ihigh=400
        message =  'Hazardous'
    elif y>=350.5 and y<=500.4 :
        clow=350.5
        chigh=500.4
        ilow=401
        ihigh=500
        message = 'Hazardous'
    else:
        x


    aqi =  ((y-clow)/(chigh-clow))*(ihigh-ilow) + ilow



    template = loader.get_template('polls/nowcast.html')
    context = {

            'c_raw_set' : cList,
            'c_tags' : cTags,
            'c_set' :c,
            'c_max' : max(c),
            'c_min' :min(c),
            'w_p' : weight_prima,
            'w' :weight,
            'nowcast' : y,
            'nowcast_message' : message,
            'aqi' : aqi
    }



    return HttpResponse(template.render(context, request))
