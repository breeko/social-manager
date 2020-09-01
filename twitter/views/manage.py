""" manage.py """

import django_tables2 as tables
from django.http import HttpResponse
from django.template import loader
from django_tables2 import A

from twitter.models import Follow, Tweet
from twitter.utils.date_utils import this_hour


def get_order_by(order_by):
  tweet_default = "scheduled"
  follow_default = "unfollow"
  tweet_fields = [f.name for f in Tweet._meta.get_fields()]
  follow_fields = [f.name for f in Follow._meta.get_fields()]
  if order_by in tweet_fields:
    return (order_by, follow_default)
  elif order_by in follow_fields:
    return (tweet_default, order_by)
  return (tweet_default, follow_default)

def manage(request):
  """ view for twitter/manage """
  template = loader.get_template('manage/index.html')
  tweets = Tweet.objects.filter(sent__isnull=True).order_by("scheduled")
  tweets_table = TweetTable(tweets)
  follows = Follow.objects.filter(unfollowed__isnull=True).order_by("-follow")
  follows_table = FollowTable(follows).paginate(page=request.GET.get("page", 1), per_page=10)

  context = {
    'tweets_table': tweets_table,
    'follows_table': follows_table,
    'title': 'Manage'
  }
  return HttpResponse(template.render(context, request))


def delete_tweets(request):
  """ Deletes a given follow id """
  ids = request.POST.getlist("ids[]", [])
  Tweet.objects.filter(id__in=ids).delete()
  return HttpResponse("{}", content_type='application/json')

def reschedule_tweets(request):
  """ Reschedules follows to occur this hour """
  ids = request.POST.getlist("ids[]", [])
  to_reschedule = Tweet.objects.filter(id__in=ids, sent__isnull=True)
  within_hours = request.POST.get("withinHours")
  print(request.POST)
  hours = float(within_hours)

  for tweet in to_reschedule:
    tweet.scheduled = this_hour(hours)
    tweet.save()
  return HttpResponse("{}", content_type='application/json')

def delete_follows(request):
  """ Deletes a given follow id """
  ids = request.POST.getlist("ids[]", [])
  Follow.objects.filter(id__in=ids).delete()
  return HttpResponse("{}", content_type='application/json')

def reschedule_follows(request):
  """ Reschedules follows to occur this hour """
  ids = request.POST.getlist("ids[]", [])
  # reschedule follows
  to_reschedule = Follow.objects.filter(id__in=ids, followed__isnull=True)
  within_hours = request.POST.get("withinHours")
  hours = float(within_hours)
  for follow in to_reschedule:
    follow.follow = this_hour(hours)
    follow.save()
  # reschedule unfollows
  to_reschedule = Follow.objects.filter(id__in=ids, followed__isnull=False, unfollowed__isnull=True)
  for follow in to_reschedule:
    follow.unfollow = this_hour(hours)
    follow.save()

  return HttpResponse("{}", content_type='application/json')

class TweetTable(tables.Table):
  tweet_selection = tables.CheckBoxColumn(accessor="pk", attrs={"th__input": {"onclick": "toggle('tweet_selection', this)"}}, orderable=False)
  edit = tables.LinkColumn('twitter:edit_tweet', text='✏️', args=[A('pk')], orderable=False, empty_values=())
  user = tables.Column(orderable=False)
  body = tables.Column(orderable=False)
  scheduled = tables.Column(orderable=False)
  sent = tables.Column(orderable=False)
  class Meta:
    attrs = {"id": "tweet_table"}

class FollowTable(tables.Table):
  follow_selection = tables.CheckBoxColumn(accessor="pk", attrs={"th__input": {"onclick": "toggle('follow_selection', this)"}}, orderable=False)
  edit = tables.LinkColumn('twitter:edit_follow', text='✏️', args=[A('pk')], orderable=False, empty_values=())
  username = tables.Column(orderable=False)
  follow = tables.Column(orderable=False)
  unfollow = tables.Column(orderable=False)
  followed = tables.Column(orderable=False)
  unfollowed = tables.Column(orderable=False)

  class Meta:
    attrs = {"id": "follow_table"}
