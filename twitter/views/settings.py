""" settings.py """
from datetime import datetime

from django import forms
from django.http import HttpResponse
from django.template import loader

from twitter.models import Tweet
from twitter.utils.date_utils import format_date

def index(request):
  """ view for settings """
  template = loader.get_template('settings/index.html')
  if request.method == "POST":
    form = NewTweetForm(request.POST)
    if form.is_valid():
      form.save(commit=True)
  form = NewTweetForm(initial={'scheduled': format_date()})
  
  context = {
    'form': form,
    'title': 'Create'
  }
  return HttpResponse(template.render(context, request))

class NewTweetForm(forms.ModelForm):
  """ Form for creating a tweet"""
  class Meta:
    model = Tweet
    fields = ('user', 'body', 'scheduled',)
