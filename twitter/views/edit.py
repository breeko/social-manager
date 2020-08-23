""" edit.py """

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.models import Tweet


def edit_tweet(request, tweet_id: int):
  """ edits a tweet """
  template = loader.get_template('edit/index.html')
  form = EditTweetForm(request.POST)
  instance = Tweet.objects.get(id=tweet_id)
  if request.method == "POST":
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
  """ Form to edit a scheduled tweet """
  class Meta:
    model = Tweet
    fields = ('body', 'scheduled',)
