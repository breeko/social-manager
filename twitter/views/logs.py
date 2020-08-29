""" logs.py """
import os

from django.http import HttpResponse
from django.template import loader


def logs(request):
  """ view for twitter/logs """
  template = loader.get_template('logs/index.html')
  path = "logs/scheduler/scheduler.log"

  logs_ = []
  if os.path.exists(path):
    with open(path) as f:
      logs_ = f.readlines()[::-1]

  context = {
    'title': "Logs",
    'logs': logs_
  }

  return HttpResponse(template.render(context, request))
