from django.shortcuts import render
from django.http import HttpResponse
from ..models import Tweet, User
from django.template import loader
from django import forms
from datetime import datetime

def create(request):
  template = loader.get_template('create/index.html')
  if (request.method == "POST"):
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
  class Meta:
    model = Tweet
    fields = ('user_id', 'body', 'scheduled',) 
  
  
