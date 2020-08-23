""" news.py """
from datetime import datetime

from django import forms
from django.http import HttpResponse
from django.template import loader

from twitter.settings import settings

from twitter.models import Tweet, User
from twitter.utils.news_utils import TOPIC_CHOICES, get_news
from twitter.utils.date_utils import format_date

def news(request):
  """ view for /twitter/news """
  template = loader.get_template('news/index.html')
  if request.method == "GET":
    suggestions = []
    form = GenerateNewsForm(initial={'sources': settings.news.default_sources, 'topic': settings.news.default_topic})
  elif request.method == "POST":
    form = GenerateNewsForm(request.POST)
    if 'generate' in request.POST:
      sources = form.data.get('sources').replace(' ', '').split(',')
      topic = form.data.get('topic')
      suggestions = get_news(sources, topic)
    elif 'save' in request.POST:
      to_save = request.POST.getlist('to_save')
      for save in to_save:
        body = request.POST.get(f"body:{save}") or ''
        username = request.POST.get(f"user:{save}")
        user = User.objects.get(username=username)
        schedule = request.POST.get(f"schedule:{save}")
        tweet_body = body + " " + save
        tweet = Tweet(user=user, body=tweet_body, scheduled=schedule)
        tweet.save()
      suggestions = []

  user_names = [u.username for u in User.objects.all()]
  context = {
    'form': form,
    'suggestions': suggestions,
    'title': 'News',
    'now': format_date(),
    'user_names': user_names
  }

  return HttpResponse(template.render(context, request))

class GenerateNewsForm(forms.Form):
  """ Form to input news sources and topic topic """
  sources = forms.CharField(label='sources', max_length=100, required=True)
  topic = forms.ChoiceField(choices=[(t, t) for t in TOPIC_CHOICES])
