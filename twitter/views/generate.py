""" generate.py """
from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from twitter.models import Tweet, User
from twitter.settings import settings
from twitter.utils.date_utils import format_date
from twitter.utils.twitter_utils import (MODEL_CHOICES, generate_tweet,
                                         get_trends)


def generate(request):
  """ view for twitter/generate """
  template = loader.get_template('generate/index.html')
  maybe_user = User.objects.first()
  if maybe_user:
    trends = get_trends(maybe_user)
  else:
    trends = []

  suggestions = []

  if request.method == "POST":
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

  generate_form = GenerateTweetForm()
  create_form = CreateTweetForm()

  user_names = [u.username for u in User.objects.all()]
  context = {
    'create_form': create_form,
    'generate_form': generate_form,
    'suggestions': suggestions,
    'title': 'Generate',
    'trends': trends,
    'user_names': user_names
  }
  return HttpResponse(template.render(context, request))

class CreateTweetForm(forms.ModelForm):
  """ Form for creating a tweet"""
  class Meta:
    model = Tweet
    fields = ('user', 'body', 'scheduled')
    widgets = {
      'body': forms.Textarea(attrs={'rows': 4}),
    }

class GenerateTweetForm(forms.Form):
  """ Form to generate tweets """
  phrase = forms.CharField(label='phrase', max_length=100, required=False)
  model = forms.CharField(
    label='model',
    widget=forms.Select(choices=MODEL_CHOICES)
  )

def submit_create_tweet(request):
  if request.method == "POST":
    form = CreateTweetForm(request.POST)
    if form.is_valid():
      form.save(commit=True)
  return HttpResponseRedirect(reverse('twitter:generate'))
