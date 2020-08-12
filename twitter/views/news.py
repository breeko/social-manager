""" news.py """
from datetime import datetime

from django import forms
from django.http import HttpResponse
from django.template import loader

from twitter.settings import NewsSettings as Settings

from ..models import Tweet, User
from ..utils.news_utils import TOPIC_CHOICES, get_news

def news(request):
  """ view for /twitter/news """
  template = loader.get_template('news/index.html')

  if request.method == "GET":
    suggestions = []
    form = GenerateNewsForm(initial={'sources': Settings.DEFAULT_NEWS_SOURCES, 'topic': Settings.DEFAULT_TOPIC})
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
        tweet_body = body + save
        tweet = Tweet(user=user, body=tweet_body, scheduled=schedule)
        tweet.save()
      suggestions = []

  user_names = [u.username for u in User.objects.all()]
  context = {
    'form': form,
    'suggestions': suggestions,
    'title': 'Generate News',
    'now': datetime.now().strftime("%Y-%m-%d %H:%M"),
    'user_names': user_names
  }

  return HttpResponse(template.render(context, request))

class GenerateNewsForm(forms.Form):
  """ Form to input news sources and topic topic """
  sources = forms.CharField(label='sources', max_length=100, required=True)
  topic = forms.ChoiceField(choices=[(t, t) for t in TOPIC_CHOICES])
