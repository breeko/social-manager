""" manage.py """

import django_tables2 as tables
from django.http import HttpResponse
from django.template import loader
from django.utils.html import format_html

from twitter.models import Follow, Tweet
from twitter.utils.date_utils import this_hour


def manage(request):
  """ view for twitter/manage """
  template = loader.get_template('manage/index.html')
  tweets = Tweet.objects.filter(sent__isnull=True)
  tweets_table = TweetTable(tweets)
  follows = Follow.objects.filter(unfollowed__isnull=True).order_by(request.GET.get("sort", "-follow"))
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
  for tweet in to_reschedule:
    tweet.scheduled = this_hour()
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
  for follow in to_reschedule:
    follow.follow = this_hour()
    follow.save()
  # reschedule unfollows
  to_reschedule = Follow.objects.filter(id__in=ids, followed__isnull=False, unfollow__isnull=True)
  for follow in to_reschedule:
    follow.unfollow = this_hour()
    follow.save()

  return HttpResponse("{}", content_type='application/json')

class TweetTable(tables.Table):
  action = tables.Column(orderable=False, empty_values=())
  user = tables.Column()
  body = tables.Column()
  scheduled = tables.Column()
  sent = tables.Column()
  def render_action(self, value, record):
    return format_html(f"""
      <span>
        <input type="checkbox" value="{record.id}">
      </span>
    """, value, record.id)
  class Meta:
    attrs = {"id": "tweet_table"}


class FollowTable(tables.Table):

  action = tables.Column(orderable=False, empty_values=())
  username = tables.Column()
  follow = tables.Column()
  unfollow = tables.Column()
  followed = tables.Column()
  unfollowed = tables.Column()

  def render_action(self, value, record):
    return format_html(f"""<input type="checkbox" value="{record.id}">""", value, record.id)
  class Meta:
    attrs = {"id": "follow_table"}
