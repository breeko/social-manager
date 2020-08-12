""" create.py """
from datetime import datetime

from django import forms
from django.http import HttpResponse
from django.template import loader

from ..models import Tweet


def create(request):
  """ view for twitter/create """
  template = loader.get_template('create/index.html')
  if request.method == "POST":
    form = NewTweetForm(request.POST)
    if form.is_valid():
      form.save(commit=True)
  form = NewTweetForm(initial={'scheduled': datetime.now().strftime("%Y-%m-%d %H:%M")})
  
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
