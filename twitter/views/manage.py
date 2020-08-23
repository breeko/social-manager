""" manage.py """
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.models import Tweet
from twitter.settings import settings


def manage(request):
  """ view for twitter/manage """
  template = loader.get_template('manage/index.html')
  sent = Tweet.objects.filter(sent__isnull=False).order_by('-scheduled')[:settings.manage.show_old]
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
