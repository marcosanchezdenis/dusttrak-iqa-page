from django.contrib import admin
from .models import Faq,AQIRange,LiteralSettings,NumericSettigs,Concentrations,MeasureData,MeasureDataView,AQINowCastHistory,History,Measurements,BackgroundTaskModel
from django.conf.urls import url
from django.http import HttpResponse
from django.contrib.auth import models
from django.contrib import messages
from background_task import background
from django.shortcuts import redirect
from django.contrib.admin import AdminSite
from django.template.response import TemplateResponse
from .tools import initDeviceConnection,getDeviceStatus,getDeviceMeasure,deviceDatetime,query_12_set_concentrations,nowcast,air_quality_index,stopDeviceMeasure,startDeviceMeasure
from django.urls import include, path
import time
from .tasks import notify_user
from datetime import datetime, timedelta
from django.db.models import Avg,Max,Min,Sum


class AQIRangeAdmin(admin.ModelAdmin):
    list_display = ['clow', 'chigh', 'ilow', 'ihigh', 'category','category_descriptor']

class FaqAdmin(admin.ModelAdmin):
    list_display = ['question', 'answer']
class LiteralSettingsAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
class NumericSettigsAdmin(admin.ModelAdmin):
    list_display = ['name', 'value']
class ConcentrationsAdmin(admin.ModelAdmin):
    list_display = ['real_start','start','final','sum','count']
    list_per_page = 15
    list_filter = ['real_start','start','final','sum','count']
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('calculate_real_time/',self.real_time),
            path('calculate_concentrations/',self.concentrations)
        ]
        return my_urls + urls
    def real_time(self,request):
        inicio = MeasureDataView.objects.latest('utimestamp').utimestamp
        final = inicio - timedelta(hours=1) -timedelta(minutes=1)
        cTags = []
        cList =[]
        ci = []
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

        average = nowcast(c)
        data, category, color =  air_quality_index(average)

        context = dict(
            nowcast=average,
            aqi= data,
            category= category,
            partitions= cList,
            concentrations=ci


        )
        return TemplateResponse(request,'admin/concentrations/real_time.html', context)




    def concentrations(self,request):
        pass

class MeasureDataAdmin(admin.ModelAdmin):
    list_display = ['elapsed_time','data','calculate_timestamp','error','alarm']
    list_per_page = 15
    list_filter = ['elapsed_time','data']
class AQINowCastHistoryAdmin(admin.ModelAdmin):
    list_display = ['timestamp','data']
    list_per_page = 15
    list_filter = ['timestamp','data']


class connectionRequestAdmin(admin.ModelAdmin):
    def get_urls(self):
        urls = super().get_urls()
        my_urls = [
            path('startrecord/',self.start_record),
            path('stoprecord/',self.stop_record),
            path('stopdevice/',self.stop_device),
            path('startdevice/',self.start_device)
        ]
        return my_urls + urls
    def start_record(self,request):
        s = initDeviceConnection()

        if s is not None:
            start_date = deviceDatetime(s)

            elapsed_time, data, error, alarm = getDeviceMeasure(s)

            measure = Measurements(
            author=models.User.objects.get(id=1) ,
            start_timestamp=start_date,
            current_timestamp=elapsed_time)
            measure.save()

            task_created = BackgroundTaskModel.objects.count()
            if not task_created:
                notify_user(measure.id,repeat=10)
            else:
                messages.add_message(request,messages.ERROR, 'Existe un proceso de grabación actualmente. ')
        else:
            messages.add_message(request,messages.ERROR, 'No se puede realizar una conexion con el Dusttrak. ')


        return redirect("admin.index");






    def stop_record(self,request):
        BackgroundTaskModel.objects.all().delete();
        return redirect('admin.index');





    def start_device(self,request):
        # BackgroundTaskModel.objects.all().delete();
        s =  initDeviceConnection()
        if s is not None:
            if startDeviceMeasure(s) :
                messages.add_message(request,messages.ERROR, 'El Dusttrak se inicio correctamente. ')
            else:
                messages.add_message(request,messages.ERROR, 'No se puede iniciar el dispositivo. ')
        else:
            messages.add_message(request,messages.ERROR, 'No se puede realizar una conexion con el Dusttrak. ')
        return redirect('admin.index');







    def stop_device(self,request):

        s =  initDeviceConnection()
        if s is not None:
            if stopDeviceMeasure(s) :
                messages.add_message(request,messages.ERROR, 'El Dusttrak se detuvo correctamente. ')
            else:
                messages.add_message(request,messages.ERROR, 'No se puede detener el dispositivo. ')
        else:
            messages.add_message(request,messages.ERROR, 'No se puede realizar una conexion con el Dusttrak. ')



        # El stop measure debe  a la vez hacer un stop recording
        # BackgroundTaskModel.objects.all().delete();
        return redirect('admin.index');














from django.views.decorators.cache import never_cache

# Register your models here.
class MyAdminSite(AdminSite):
    
    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        app_list = self.get_app_list(request)


        s = initDeviceConnection()
        if s==None :
            messages.add_message(request,messages.ERROR, 'No se puede realizar una conexion con el Dusttrak. ')

        context = dict(
            self.each_context(request),
            title=self.index_title,
            app_list=app_list,
            device_datetime =  "Sin Conexion" if s==None else deviceDatetime(s),
            device_status= "Sin Conexion" if s==None else getDeviceStatus(s),
            record_status=BackgroundTaskModel.objects.all(),
            conf_correction_index =  NumericSettigs.objects.all().filter(name='conf_correction_index').first().value,
            link_stop_device='/admin/polls/history/stopdevice',
            link_stop_record='/admin/polls/history/stoprecord',
            link_start_device='/admin/polls/history/startdevice',
            link_start_record='/admin/polls/history/startrecord'

        )
        context.update(extra_context or {})

        request.current_app = self.name

        return TemplateResponse(request, self.index_template or 'admin/index.html', context)
#


# Customize admin site

admin.site = MyAdminSite()







admin.site.register(Faq,FaqAdmin)
admin.site.register(AQIRange,AQIRangeAdmin)
admin.site.register(NumericSettigs,NumericSettigsAdmin)
admin.site.register(LiteralSettings,LiteralSettingsAdmin)
admin.site.register(Concentrations,ConcentrationsAdmin)

admin.site.register(MeasureData,MeasureDataAdmin)
admin.site.register(AQINowCastHistory,AQINowCastHistoryAdmin)
admin.site.register(History,connectionRequestAdmin)
admin.site.site_header = 'Dusttrak'
admin.site.site_title = 'Opciones'
admin.site.index_title  = 'Opciones'
