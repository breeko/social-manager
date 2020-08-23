""" logs.py """
from django.http import HttpResponse
from django.template import loader
import os

def logs(request):
  """ view for twitter/logs """
  template = loader.get_template('logs/index.html')
  path = "scheduler.log"

  logs = []
  if os.path.exists(path):
    with open(path) as f:
      logs = f.readlines()[::-1]

  context = {
    'title': "Logs",
    'logs': logs
  }

  return HttpResponse(template.render(context, request))
