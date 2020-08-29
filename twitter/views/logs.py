""" logs.py """
import os

from django.http import HttpResponse
from django.template import loader

from twitter.management.commands.scheduler import STATUS_PATH, LOGGING_PATH

def logs(request):
  """ view for twitter/logs """
  template = loader.get_template('logs/index.html')

  status = None
  if os.path.exists(STATUS_PATH):
    with open(STATUS_PATH) as f:
      status = f.read()

  logs_ = []
  if os.path.exists(LOGGING_PATH):
    with open(LOGGING_PATH) as f:
      logs_ = f.readlines()[::-1]

  context = {
    'title': "Logs",
    'logs': logs_,
    'status': status
  }

  return HttpResponse(template.render(context, request))
