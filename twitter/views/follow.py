""" follow.py """
from datetime import datetime, timedelta

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.models import Follow, User
from twitter.settings import settings

from ..utils.twitter_utils import create_valid_user, get_suggestions

def follow(request):
  """ form to generate follows """
  template = loader.get_template('follow/index.html')
  usernames = [u.username for u in User.objects.all()]

  follow_form = FollowTweetForm(initial=FollowTweetFormDefaults)

  suggestions = []
  if request.method == 'POST':
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    follow_form = FollowTweetForm(request.POST)
    if 'suggest' in request.POST:
      valid_user = create_valid_user(
        blacklist=follow_form.data.get('blacklist'),
        followers_max=follow_form.data.get('followers_max'),
        followers_min=follow_form.data.get('followers_min'),
        friends_max=follow_form.data.get('friends_max'),
        friends_min=follow_form.data.get('friends_min'),
        followers_friend_ratio_min=follow_form.data.get('followers_friend_ratio_min'),
        followers_friend_ratio_max=follow_form.data.get('followers_friend_ratio_max')
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
        follow_.save()

  now = datetime.now()
  follow_date = now.strftime("%Y-%m-%d %H:%M")
  unfollow_date = None if settings.follow.unfollow_default_days is None else \
    (now + timedelta(days=settings.follow.unfollow_default_days)).strftime("%Y-%m-%d %H:%M")

  pending = Follow.objects.filter(unfollowed__isnull=True)
  context = {
    'follow_form': follow_form,
    'title': "Follow",
    'suggestions': suggestions,
    'usernames': usernames,
    'follow_date': follow_date,
    'unfollow_date': unfollow_date,
    'pending': pending
  }
  return HttpResponse(template.render(context, request))

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

def delete_follow(request, pk: int):
  """ Deletes a given follow id """
  to_delete = Follow.objects.get(id=pk)
  if to_delete:
    to_delete.delete()
  return HttpResponseRedirect(reverse('twitter:follow'))
