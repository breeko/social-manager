from django import forms
from django.http import HttpResponse
from django.template import loader
from ..utils.twitter_utils import get_suggestions, create_valid_user
from twitter.models import User, Follow
from datetime import datetime, timedelta
from social.settings import UNFOLLOW_DEFAULT_DAYS

def follow(request):
  NUM_SUGGESTIONS = 5

  template = loader.get_template('follow/index.html')
  usernames = [u.username for u in User.objects.all()]

  form = FollowTweetForm()
  suggestions = []
  if (request.method == 'POST'):
    username = request.POST.get('username')
    user = User.objects.get(username=username)
    form = FollowTweetForm(request.POST)
    if 'suggest' in request.POST:
      valid_user = create_valid_user(
        followers_max=int(form.data.get('followers_max')),
        followers_min=int(form.data.get('followers_min')),
        friends_max=int(form.data.get('friends_max')),
        friends_min=int(form.data.get('friends_min')),
        followers_friend_ratio_min=float(form.data.get('followers_friend_ratio_min')),
        followers_friend_ratio_max=float(form.data.get('followers_friend_ratio_max')),
      )
      suggestions = get_suggestions(user, valid_user, NUM_SUGGESTIONS)
    elif 'save' in request.POST:
      to_save = request.POST.getlist('to_save')
      for s in to_save:        
        follow = request.POST.get(f"follow:{s}")
        unfollow = request.POST.get(f"unfollow:{s}")
        follow = Follow(username=s, user=user, follow=follow, unfollow=unfollow)
        follow.save()

  user_names = [u.username for u in User.objects.all()]
  now = datetime.now()
  later = now + timedelta(days=UNFOLLOW_DEFAULT_DAYS)

  context = {
    'form': form,
    'title': "Follow",
    'suggestions': suggestions,
    'usernames': usernames,
    'now': now.strftime("%Y-%m-%d %H:%M"),
    'later': later.strftime("%Y-%m-%d %H:%M")
  }

  return HttpResponse(template.render(context, request))


class FollowTweetForm(forms.Form):
  followers_min = forms.IntegerField(label="Min followers")
  followers_max = forms.IntegerField(label="Max followers")
  friends_min = forms.IntegerField(label="Min friends")
  friends_max = forms.IntegerField(label="Max friends")
  followers_friend_ratio_min = forms.FloatField(label="Max followers to friends ratio")
  followers_friend_ratio_max = forms.FloatField(label="Min followers to friends ratio")
  