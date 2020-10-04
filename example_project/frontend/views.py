from django.shortcuts import HttpResponse, render
from django.conf import settings


def home(request):
    return render(request, 'frontend/index.html')
    # return HttpResponse(settings.WEBPACK_SETTINGS.get('output_dir'))
