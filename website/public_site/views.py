
import requests
from django.template import loader
from django.http import HttpResponse




from public_site.models import AQIRange,Faq,AQINowCastHistory,LiteralSettings

# Create your views here.




def index(request):
    aqi = AQINowCastHistory.objects.all().last()




    template = loader.get_template('public_site/index.html')

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
        'home_ica_pm25_message': LiteralSettings.objects.all().filter(name='home_ica_pm25_message').first().value,
        'HOME_LABEL': LiteralSettings.objects.all().filter(name='HOME_LABEL').first().value,
        'INTRO_LABEL': LiteralSettings.objects.all().filter(name='INTRO_LABEL').first().value,
        'LOCALIZATION_LABEL': LiteralSettings.objects.all().filter(name='LOCALIZATION_LABEL').first().value,
        'SCALE_LABEL': LiteralSettings.objects.all().filter(name='SCALE_LABEL').first().value,
        'DISCLAIMER_LABEL': LiteralSettings.objects.all().filter(name='DISCLAIMER_LABEL').first().value,
        'FAQ_LABEL': LiteralSettings.objects.all().filter(name='FAQ_LABEL').first().value,
        'HOME_BRAND': LiteralSettings.objects.all().filter(name='HOME_BRAND').first().value,
        'HOME_TITLE1': LiteralSettings.objects.all().filter(name='HOME_TITLE1').first().value,
        'HOME_TITLE2': LiteralSettings.objects.all().filter(name='HOME_TITLE2').first().value,
        'HOME_TITLE3': LiteralSettings.objects.all().filter(name='HOME_TITLE3').first().value,
        'HOME_TOOLS': LiteralSettings.objects.all().filter(name='HOME_TOOLS').first().value,
        'INTRO_TITLE': LiteralSettings.objects.all().filter(name='INTRO_TITLE').first().value,
                'INTRO_CONTENT': LiteralSettings.objects.all().filter(name='INTRO_CONTENT').first().value,
        'LOCALIZATION_MAP': LiteralSettings.objects.all().filter(name='LOCALIZATION_MAP').first().value,
        'LOCALIZATION_TITLE': LiteralSettings.objects.all().filter(name='LOCALIZATION_TITLE').first().value,
        'LOCALIZATION_CONTENT': LiteralSettings.objects.all().filter(name='LOCALIZATION_CONTENT').first().value,
        'SCALE_TITLE': LiteralSettings.objects.all().filter(name='SCALE_TITLE').first().value,
        'SCALE_CONTENT': LiteralSettings.objects.all().filter(name='SCALE_CONTENT').first().value,
        'DISCLAIMER_TITLE': LiteralSettings.objects.all().filter(name='DISCLAIMER_TITLE').first().value,
        'DISCLAIMER_CONTENT': LiteralSettings.objects.all().filter(name='DISCLAIMER_CONTENT').first().value,
        'FAQ_TITLE': LiteralSettings.objects.all().filter(name='FAQ_TITLE').first().value,
        'FAQ_CONTENT': LiteralSettings.objects.all().filter(name='FAQ_CONTENT').first().value,
        'FOOTER_MESSAGE': LiteralSettings.objects.all().filter(name='FOOTER_MESSAGE').first().value,
        'FOOTER_SIGNATURE': LiteralSettings.objects.all().filter(name='FOOTER_SIGNATURE').first().value,


    }

    return HttpResponse(template.render(context, request))
