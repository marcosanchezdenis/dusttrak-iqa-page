from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='polls.index'),
    path('startrecord', views.start_record, name='load'),
    path('stoprecord', views.stop_record, name='load'),
    path('measuredata', views.measuredata, name='measuredata'),
    path('calculate', views.calculate, name='calculate'),
    path('calculate2', views.calculate_concentrations, name='concentrations'),
]
