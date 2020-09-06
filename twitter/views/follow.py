""" follow.py """
from datetime import timedelta

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.utils import timezone

from twitter.models import Follow, User
from twitter.settings import settings
from twitter.utils.date_utils import read_date, randomize_date
from twitter.utils.twitter_utils import create_valid_user, get_suggestions


def get_unfollow_date():
  if settings.follow.unfollow_default_days is None:
    return None
  return timezone.now() + timedelta(days=settings.follow.unfollow_default_days)

def follow(request):
  """ form to generate follows """
  template = loader.get_template('follow/index.html')
  usernames = [u.username for u in User.objects.all()]

  bulk_form = BulkFollowForm()
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
      follows = []
      for s in to_save:
        to_follow = request.POST.get(f"follow:{s}")
        to_unfollow = request.POST.get(f"unfollow:{s}")
        if to_unfollow == "None":
          follow_ = Follow(username=s, user=user, follow=to_follow)
        else:
          follow_ = Follow(username=s, user=user, follow=to_follow, unfollow=to_unfollow)
        follows.append(follow_)
      Follow.objects.bulk_create(follows)

  follow_date = timezone.now()
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
  follow_dt = forms.DateTimeField(label="Follow", required=True, initial=timezone.now())
  unfollow_dt = forms.DateTimeField(label="Unfollow", required=False, initial=get_unfollow_date())
  within_hour = forms.FloatField(label="Within hour", required=True, min_value=0.0, initial=1.0)

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
  "since": timezone.now() - timedelta(days=1),
  "blacklist": settings.follow.default_blacklist
}

def bulk_follow(request):
  """ Handles bulk follow """
  if request.method == 'POST':
    username = request.POST.get('bulk_username')
    user = User.objects.get(username=username)
    hours = float(request.POST.get('within_hour'))
    # exclude_followed = request.POST.get('exclude_followed')
    print(request.POST)
    for u in request.POST.get('users').split("\n"):
      to_follow = u.strip()
      follow_date = read_date(request.POST.get('follow_dt'))
      follow_date = randomize_date(dt=follow_date, hours=hours)
      unfollow_date = None if request.POST.get('unfollow_dt') is None else \
        randomize_date(dt=read_date(request.POST.get('unfollow_dt')), hours=hours)

      if not Follow.objects.filter(username=to_follow).exists():
        Follow(username=to_follow, user=user, follow=follow_date, unfollow=unfollow_date).save()
  return HttpResponseRedirect(reverse('twitter:follow'))
