""" follow.py """
from datetime import datetime, timedelta
from random import random

from django import forms
from django.db.utils import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.models import Follow, User
from twitter.settings import settings
from twitter.utils.date_utils import format_date, read_date
from twitter.utils.twitter_utils import create_valid_user, get_suggestions


def get_unfollow_date():
  if settings.follow.unfollow_default_days is None:
    return None 
  return format_date(datetime.now() + timedelta(days=settings.follow.unfollow_default_days))

def follow(request):
  """ form to generate follows """
  template = loader.get_template('follow/index.html')
  usernames = [u.username for u in User.objects.all()]

  bulk_form = BulkFollowForm(initial=BulkFollowFormDefaults)
  follow_form = FollowTweetForm(initial=FollowTweetFormDefaults)

  suggestions = []
  if request.method == 'POST':
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    follow_form = FollowTweetForm(request.POST)
    if 'suggest' in request.POST:
      expressions = [
        f"followers_count <= {follow_form.data.get('followers_max') or 2**32}",
        f"followers_count >= {follow_form.data.get('followers_min') or 0}",
        f"friends_count <= {follow_form.data.get('friends_max') or 2**32}",
        f"friends_count >= {follow_form.data.get('friends_min') or 0}",
        f"followers_count / ( friends_count + 1 ) <= {follow_form.data.get('followers_friend_ratio_max') or 2**32}",
        f"followers_count / ( friends_count + 1 ) >= {follow_form.data.get('followers_friend_ratio_min') or 0}"
      ]
      valid_user = create_valid_user(
        blacklist=follow_form.data.get('blacklist'),
        expressions=expressions
      )
      hashtag = follow_form.data.get("hashtag")
      since = follow_form.data.get("since")
      suggestions = \
        get_suggestions(user, hashtag, valid_user, since, settings.follow.num_suggestions)
    elif 'save' in request.POST:
      to_save = request.POST.getlist('to_save')
      for s in to_save:
        to_follow = request.POST.get(f"follow:{s}")
        to_unfollow = request.POST.get(f"unfollow:{s}")
        if to_unfollow == "None":
          follow_ = Follow(username=s, user=user, follow=to_follow)
        else:
          follow_ = Follow(username=s, user=user, follow=to_follow, unfollow=to_unfollow)

        try:
          follow_.save()
        except IntegrityError:
          # user has already been followed or queued to be followed
          continue

  follow_date = format_date()
  unfollow_date = get_unfollow_date()
  context = {
    'bulk_form': bulk_form,
    'follow_form': follow_form,
    'title': "Follow",
    'suggestions': suggestions,
    'usernames': usernames,
    'follow_date': follow_date,
    'unfollow_date': unfollow_date
  }
  return HttpResponse(template.render(context, request))

class BulkFollowForm(forms.Form):
  users = forms.CharField(label="Users", widget=forms.Textarea(attrs={"rows": 5, "cols": 20}))
  unfollow = forms.DateField(label="Unfollow", required=False)
  
BulkFollowFormDefaults = {
  "unfollow": get_unfollow_date()
}

class FollowTweetForm(forms.Form):
  hashtag = forms.CharField(label="Hashtag", required=True)
  blacklist = forms.CharField(label="Blacklist profile words", required=False)
  followers_min = forms.IntegerField(label="Min followers", required=False)
  followers_max = forms.IntegerField(label="Max followers", required=False)
  friends_min = forms.IntegerField(label="Min friends", required=False)
  friends_max = forms.IntegerField(label="Max friends", required=False)
  followers_friend_ratio_min = forms.FloatField(label="Min followers/friends", required=False)
  followers_friend_ratio_max = forms.FloatField(label="Max followers/friends", required=False)
  since = forms.DateField(label="Since", required=True)

FollowTweetFormDefaults = {
  "since": datetime.now() - timedelta(days=1),
  "blacklist": settings.follow.default_blacklist
}

def bulk_follow(request):
  if request.method == 'POST':
    username = request.POST.get('bulk_username')
    user = User.objects.get(username=username)
    unfollow = request.POST.get('unfollow')
    for u in request.POST.get('users').split("\n"):
      to_follow = u.strip()
      unfollow_random = read_date(unfollow) + timedelta(hours=random())
      follow_random = datetime.now() + timedelta(hours=random())
      if not Follow.objects.filter(username=to_follow).exists():
        Follow(username=to_follow, user=user, follow=follow_random, unfollow=unfollow_random).save()
  return HttpResponseRedirect(reverse('twitter:follow'))
