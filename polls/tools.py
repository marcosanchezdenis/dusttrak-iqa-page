import socket
from datetime import datetime,timedelta
from polls.models import AQIRange,Concentrations

def deviceDatetime(socket1):
    socket1.send('RSDATETIME\r'.encode())
    datetimeb = socket1.recv(1024)
    info = datetimeb.decode('UTF-8')
    return datetime.strptime(info,"\r\n%m/%d/%Y,%H:%M:%S\r\n")

def initDeviceConnection():
    HOST = '172.16.5.2'    # The remote host
    PORT = 3602              # The same port as used by the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s

def getDeviceStatus(socket1):
    socket1.send('MSTATUS\r'.encode())
    statusb = socket1.recv(1024)
    return statusb.decode('UTF-8')


def getDeviceMeasure(socket):
    socket.send('RMLOGGEDMEAS\r'.encode())
    data = socket.recv(1024)
    info = data.decode('UTF-8').split(",")

    if len(info) == 2:
        return info[0].rstrip(), info[1].rstrip(), None, None
    if len(info) == 3:
        return info[0].rstrip(), info[1].rstrip(), info[2].rstrip(),None
    if len(info) == 4:
        return info[0].rstrip(), info[1].rstrip(), info[2].rstrip(),info[3].rstrip(),


def nowcast(c):
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
    return  sum_sup/sum_inf


def air_quality_index(average):
    range = AQIRange.objects.all();
    for category in range:
        if average >= category.clow and average <= category.chigh :
            return  ((average-category.clow)/(category.chigh-category.clow))*(category.ihigh-category.ilow) + category.ilow , category.category, category.color

def query_12_set_concentrations(current_time):
    last_concentration_hour = current_time - timedelta(minutes=current_time.minute) - timedelta(seconds=current_time.second) - timedelta(hours=1)
    back_12_hour =  last_concentration_hour - timedelta(hours=12)

    set_12_hours = Concentrations.objects.all().filter(start__lte=last_concentration_hour,final__gte=back_12_hour)[:12]
    c=[]
    if set_12_hours.exists():
        for c_hour in set_12_hours:
            c.append(c_hour.data*1000*0.38)
    return c
