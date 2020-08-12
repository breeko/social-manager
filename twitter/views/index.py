""" index.py """
from django.http import HttpResponse
from django.template import loader

def index(request):
    """ view for twitter """
    template = loader.get_template('index.html')
    return HttpResponse(template.render({'title': 'Menu'}, request))
