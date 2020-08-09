from django.shortcuts import render
from django.http import HttpResponse
from ..models import Tweet, User
from django.template import loader
from django import forms
from bootstrap_datepicker_plus import DatePickerInput
from ..utils.twitter_utils import generate_tweet, get_trends
from django.utils import timezone
from datetime import datetime

def generate(request):
  NUM_SUGGESTIONS = 2

  template = loader.get_template('generate/index.html')
  maybe_user = User.objects.first()
  if maybe_user:
    trends = get_trends(maybe_user)
  else:
    trends = []

  if (request.method == "GET"):
    suggestions = []
    form = GenerateTweetForm()
  elif (request.method == "POST"):
    form = GenerateTweetForm(request.POST)
    if 'generate' in request.POST:
      keyword = form.data.get('keyword', '')
      suggestions = [generate_tweet(keyword) for _ in range(NUM_SUGGESTIONS)]
    if 'trend' in request.POST:
      trend = request.POST['trend']
      print(trend)
      form = GenerateTweetForm(initial={'keyword': trend})
      suggestions = [generate_tweet(trend) for _ in range(NUM_SUGGESTIONS)]
    elif 'save' in request.POST:
      key = request.POST['save']
      checks = [k for k in request.POST.keys() if k.startswith('check')]
      for check in checks:
        key = check.split(":")[-1]
        body = request.POST.get(f"body:{key}")
        username = request.POST.get(f"user:{key}")
        user = User.objects.get(username=username)
        schedule = request.POST.get(f"schedule:{key}")
        tweet = Tweet(user_id=user, body=body, scheduled=schedule)
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
  keyword = forms.CharField(label='keyword', max_length=100, required=False)

