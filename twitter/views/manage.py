""" manage.py """
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.settings import ManageSettings as Settings

from ..models import Tweet

def manage(request):
  """ view for twitter/manage """
  template = loader.get_template('manage/index.html')
  sent = Tweet.objects.filter(sent__isnull=False).order_by('-scheduled')[:Settings.SHOW_OLD]
  not_sent = Tweet.objects.filter(sent__isnull=True)
  tweets = sent | not_sent

  context = {
    'tweets': tweets.order_by('scheduled'),
    'delete_tweet': delete_tweet,
    'title': 'Manage'
  }
  return HttpResponse(template.render(context, request))

def delete_tweet(request, pk):
  """ deletes tweet from queue """
  tweet = Tweet.objects.get(id=pk)
  if tweet:
    tweet.delete()
  return HttpResponseRedirect(reverse('twitter:manage'))
