from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from ..models import Tweet, User
from django.template import loader
from django import forms
from django.urls import reverse


def edit_tweet(request, tweet_id: int):
  template = loader.get_template('edit/index.html')
  form = EditTweetForm(request.POST)
  instance = Tweet.objects.get(id=tweet_id)
  if (request.method == "POST"):
    form = EditTweetForm(request.POST, instance=instance)
    if form.is_valid():
      form.save(commit=True)
      return HttpResponseRedirect(reverse('twitter:manage'))
  else:
    form = EditTweetForm(instance=instance)
  
  context = {
    'tweet_id': tweet_id,
    'form': form,
    'title': 'Edit'
  }
  return HttpResponse(template.render(context, request))

class EditTweetForm(forms.ModelForm):
  class Meta:
    model = Tweet
    fields = ('body', 'scheduled',)
  
