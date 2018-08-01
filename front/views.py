
import requests
from django.template import loader
from django.http import HttpResponse
from polls.models import AQIRange,Faq,AQINowCastHistory,LiteralSettings

# Create your views here.




def index(request):
    aqi = AQINowCastHistory.objects.all().last()




    template = loader.get_template('front/index.html')

    # controlar errores cuando no se tiene los registros, o no permitir que sea borrados
    context = {
        'list_faq': Faq.objects.all(),
        'list_aqirange': AQIRange.objects.all(),
        'aqi': AQINowCastHistory.objects.all().last(),
        'aqi_info' : AQIRange.objects.all().filter(ilow__lte=int(aqi.data),ihigh__gte=int(aqi.data)).first(),
        'aviso_uso_title': LiteralSettings.objects.all().filter(name='aviso_uso_title').first().value,
        'aviso_uso_body': LiteralSettings.objects.all().filter(name='aviso_uso_body').first().value,
        'localizacion_title': LiteralSettings.objects.all().filter(name='localizacion_title').first().value,
        'localizacion_body': LiteralSettings.objects.all().filter(name='localizacion_body').first().value,
        'home_ica_pm25_message': LiteralSettings.objects.all().filter(name='home_ica_pm25_message').first().value


    }

    return HttpResponse(template.render(context, request))
