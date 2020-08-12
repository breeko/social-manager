from django import forms
from django.http import HttpResponse
from django.template import loader
from ..utils.twitter_utils import get_suggestions, create_valid_user
from twitter.models import User, Follow
from datetime import datetime, timedelta
from twitter.settings import UNFOLLOW_DEFAULT_DAYS, LAST_TWEET_DAYS
from django.forms.models import formset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout
from django.forms.models import inlineformset_factory
from crispy_forms.bootstrap import InlineField
from twitter.settings import NUM_FOLLOW_SUGGESTIONS

def follow(request):
  template = loader.get_template('follow/index.html')
  usernames = [u.username for u in User.objects.all()]

  follow_form = FollowTweetForm(initial=FollowTweetFormDefaults)

  suggestions = []
  if (request.method == 'POST'):
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    follow_form = FollowTweetForm(request.POST)
    if 'suggest' in request.POST:
      valid_user = create_valid_user(
        followers_max=follow_form.data.get('followers_max'),
        followers_min=follow_form.data.get('followers_min'),
        friends_max=follow_form.data.get('friends_max'),
        friends_min=follow_form.data.get('friends_min'),
        followers_friend_ratio_min=follow_form.data.get('followers_friend_ratio_min'),
        followers_friend_ratio_max=follow_form.data.get('followers_friend_ratio_max'),
        last_tweet=follow_form.data.get('last_tweet'),
      )
      suggestions = get_suggestions(user, valid_user, NUM_FOLLOW_SUGGESTIONS)
    elif 'save' in request.POST:
      to_save = request.POST.getlist('to_save')
      for s in to_save:
        to_follow = request.POST.get(f"follow:{s}")
        to_unfollow = request.POST.get(f"unfollow:{s}")
        follow_ = Follow(username=s, user=user, follow=to_follow, unfollow=to_unfollow)
        follow_.save()

  user_names = [u.username for u in User.objects.all()]
  now  = datetime.now()
  follow_date = now
  unfollow_date = None if UNFOLLOW_DEFAULT_DAYS is None else now + timedelta(days=UNFOLLOW_DEFAULT_DAYS)

  context = {
    'follow_form': follow_form,
    'title': "Follow",
    'suggestions': suggestions,
    'usernames': usernames,
    'follow_date': follow_date.strftime("%Y-%m-%d %H:%M"),
    'unfollow_date': unfollow_date.strftime("%Y-%m-%d %H:%M")
  }
  return HttpResponse(template.render(context, request))

class FollowTweetForm(forms.Form):
  followers_min = forms.IntegerField(label="Min followers", required=False)
  followers_max = forms.IntegerField(label="Max followers", required=False)
  friends_min = forms.IntegerField(label="Min friends", required=False)
  friends_max = forms.IntegerField(label="Max friends", required=False)
  followers_friend_ratio_min = forms.FloatField(label="Min followers/friends", required=False)
  followers_friend_ratio_max = forms.FloatField(label="Max followers/friends", required=False)
  last_tweet = forms.DateField(label="Last tweet", required=False)

FollowTweetFormDefaults = {
  "last_tweet":   None if LAST_TWEET_DAYS is None else datetime.now() - timedelta(days=LAST_TWEET_DAYS)
}