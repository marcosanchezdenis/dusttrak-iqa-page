from django.db import models
from django.conf import settings
from datetime import datetime,timedelta

class Measurements(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    start_timestamp = models.DateTimeField()
    current_timestamp = models.IntegerField()



class MeasureData(models.Model) :
    class Meta:
        verbose_name = 'Concentracion 300 segundos'
        verbose_name_plural = 'Concentraciones 300 segundos'
    elapsed_time  = models.IntegerField()
    data = models.FloatField()
    measurements =  models.ForeignKey(Measurements, on_delete=models.CASCADE)
    error = models.TextField(default=None, blank=True, null=True)
    alarm = models.TextField(default=None, blank=True, null=True)
    @property
    def calculate_timestamp(self):
      return self.measurements.start_timestamp + timedelta(seconds=(self.elapsed_time - self.measurements.current_timestamp))


class MeasureDataView(models.Model):
    class Meta:
            db_table = 'fullmeasure'
            managed = False
    elapsed_time = models.IntegerField()
    data = models.FloatField()
    measurements = models.ForeignKey(Measurements, on_delete=models.CASCADE)
    utimestamp = models.DateTimeField()



class History(models.Model):
    author = models.ForeignKey(settings.AUTH_USER_MODEL,on_delete=models.CASCADE)
    action = models.TextField()
    datetime = models.DateTimeField()


class BackgroundTaskModel(models.Model):
    class Meta:
        db_table = 'background_task';
        managed = False
    task_params = models.TextField()
    task_hash = models.CharField(max_length=40)
    repeat = models.BigIntegerField()
    repeat_until = models.DateTimeField()
    task_name = models.CharField(max_length=190)


class Concentrations(models.Model):
    class Meta:
        verbose_name = 'Concentracion horaria'
        verbose_name_plural = 'Concentraciones horarias'
    real_start = models.DateTimeField()
    start = models.DateTimeField()
    final =  models.DateTimeField()
    sum = models.FloatField()
    count = models.IntegerField()
    @property
    def data(self):
        return self.sum / self.count



class Faq(models.Model):
    class Meta:
        verbose_name = 'Pregunta Frecuente'
        verbose_name_plural = 'Preguntas frecuentes'
    question = models.CharField(max_length=250)
    answer  = models.TextField()
    publish = models.BooleanField()
    created_at = models.DateTimeField()

class AQIRange(models.Model):
    class Meta:
        verbose_name = 'Rango de calidad de Aire'
        verbose_name_plural = 'Rangos de calidad de Aire'
    clow = models.FloatField()
    chigh = models.FloatField()
    ilow = models.FloatField()
    ihigh = models.FloatField()
    category = models.CharField(max_length=250)
    category_descriptor = models.TextField()
    color = models.CharField(max_length=150)

class AQINowCastHistory(models.Model):
    class Meta:
        verbose_name = 'ICA de hora'
        verbose_name_plural = 'Historial ICA'
    timestamp = models.DateTimeField();
    data = models.FloatField()


class NumericSettigs(models.Model):
    class Meta:
        verbose_name = 'Configuracion numerica'
        verbose_name_plural = 'Configuraciones numericas'
    name = models.CharField(max_length=255)
    value =  models.FloatField()

class LiteralSettings(models.Model):
    class Meta:
        verbose_name = 'Configuracion literal'
        verbose_name_plural = 'Configuraciones literales'
    name  = models.CharField(max_length=255)
    value = models.TextField()

# Create your models here.
