""" generate.py """
from datetime import datetime

from django import forms
from django.http import HttpResponse
from django.template import loader

from twitter.settings import settings

from ..models import Tweet, User
from ..utils.twitter_utils import MODEL_CHOICES, generate_tweet, get_trends


def generate(request):
  """ view for twitter/generate """
  template = loader.get_template('generate/index.html')
  maybe_user = User.objects.first()
  if maybe_user:
    trends = get_trends(maybe_user)
  else:
    trends = []

  if request.method == "GET":
    suggestions = []
    form = GenerateTweetForm()
  elif request.method == "POST":
    form = GenerateTweetForm(request.POST)
    if 'generate' in request.POST:
      phrase = form.data.get('phrase', '')
      model = form.data.get('model')
      suggestions = [generate_tweet(phrase, model) for _ in range(settings.generate.num_suggestions)]
    elif 'trend' in request.POST:
      trend = request.POST['trend']
      model = form.data.get('model')
      form = GenerateTweetForm(initial={'phrase': trend})
      suggestions = [generate_tweet(trend, model) for _ in range(settings.generate.num_suggestions)]
    elif 'save' in request.POST:
      key = request.POST['save']
      checks = [k for k in request.POST.keys() if k.startswith('check')]
      for check in checks:
        key = check.split(":")[-1]
        body = request.POST.get(f"body:{key}")
        username = request.POST.get(f"user:{key}")
        user = User.objects.get(username=username)
        schedule = request.POST.get(f"schedule:{key}")
        tweet = Tweet(user=user, body=body, scheduled=schedule)
        tweet.save()
      suggestions = []

  user_names = [u.username for u in User.objects.all()]
  context = {
    'form': form,
    'suggestions': suggestions,
    'title': 'Generate',
    'now': datetime.now().strftime("%Y-%m-%d %H:%M"),
    'trends': trends,
    'user_names': user_names
  }

  return HttpResponse(template.render(context, request))

class GenerateTweetForm(forms.Form):
  phrase = forms.CharField(label='phrase', max_length=100, required=False)
  model = forms.CharField(
    label='model',
    widget=forms.Select(choices=MODEL_CHOICES)
  )
