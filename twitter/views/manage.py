""" manage.py """

import django_tables2 as tables
from cron_descriptor import ExpressionDescriptor
from django.http import HttpResponse
from django.template import loader
from django_tables2 import A

from twitter.models import AutoFollow, Follow, Tweet
from twitter.utils.date_utils import randomize_date


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
  follows = Follow.objects.filter(unfollowed__isnull=True).order_by("follow")
  auto_follows = AutoFollow.objects.all()
  follows_table = FollowTable(follows).paginate(page=request.GET.get("page", 1), per_page=10)
  auto_follows_table = AutoFollowTable(auto_follows).paginate(page=request.GET.get("page", 1), per_page=10)

  context = {
    'tweets_table': tweets_table,
    'follows_table': follows_table,
    'auto_follows_table': auto_follows_table,
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
  hours = float(within_hours)

  for tweet in to_reschedule:
    tweet.scheduled = randomize_date(hours=hours)
    tweet.save()
  return HttpResponse("{}", content_type='application/json')

def delete_follows(request):
  """ Deletes a given follow id """
  ids = request.POST.getlist("ids[]", [])
  Follow.objects.filter(id__in=ids).delete()
  return HttpResponse("{}", content_type='application/json')

def delete_auto_follows(request):
  """ Deletes a given follow id """
  ids = request.POST.getlist("ids[]", [])
  AutoFollow.objects.filter(id__in=ids).delete()
  return HttpResponse("{}", content_type='application/json')

def reschedule_follows(request):
  """ Reschedules follows to occur this hour """
  ids = request.POST.getlist("ids[]", [])
  # reschedule follows
  to_reschedule = Follow.objects.filter(id__in=ids, followed__isnull=True)
  within_hours = request.POST.get("withinHours")
  hours = float(hours=within_hours)
  for follow in to_reschedule:
    follow.follow = randomize_date(hours=hours)
    follow.save()
  # reschedule unfollows
  to_reschedule = Follow.objects.filter(id__in=ids, followed__isnull=False, unfollowed__isnull=True)
  for follow in to_reschedule:
    follow.unfollow = randomize_date(hours=hours)
    follow.save()

  return HttpResponse("{}", content_type='application/json')

class TweetTable(tables.Table):
  tweet_selection = tables.CheckBoxColumn(accessor="pk", attrs={"th__input": {"onclick": "toggle('tweet_selection', this)"}}, orderable=False)
  _ = tables.LinkColumn('twitter:edit_tweet', text='✏️', args=[A('pk')], orderable=False, empty_values=())
  user = tables.Column(orderable=False)
  body = tables.Column(orderable=False)
  scheduled = tables.Column(orderable=False)
  sent = tables.Column(orderable=False)
  class Meta:
    attrs = {"id": "tweet_table"}

class FollowTable(tables.Table):
  follow_selection = tables.CheckBoxColumn(accessor="pk", attrs={"th__input": {"onclick": "toggle('follow_selection', this)"}}, orderable=False)
  _ = tables.LinkColumn('twitter:edit_follow', text='✏️', args=[A('pk')], orderable=False, empty_values=())
  user = tables.Column(orderable=False)
  username = tables.Column(orderable=False)
  follow = tables.Column(orderable=False)
  unfollow = tables.Column(orderable=False)
  followed = tables.Column(orderable=False)
  unfollowed = tables.Column(orderable=False)

  class Meta:
    attrs = {"id": "follow_table"}

class AutoFollowTable(tables.Table):
  auto_follow_selection = tables.CheckBoxColumn(accessor="pk", attrs={"th__input": {"onclick": "toggle('auto_follow_selection', this)"}}, orderable=False)
  _ = tables.LinkColumn('twitter:edit_auto_follow', text='✏️', args=[A('pk')], orderable=False, empty_values=())
  user = tables.Column(orderable=False)
  path = tables.Column(orderable=False)
  count = tables.Column(orderable=False)
  over_hours = tables.Column(orderable=False)
  unfollow_days = tables.Column(orderable=False)
  schedule = tables.Column(orderable=False)

  def render_schedule(self, value: str):
    return ExpressionDescriptor(value, throw_exception_on_parse_error=False)

  class Meta:
    attrs = {"id": "auto_follow_table"}
