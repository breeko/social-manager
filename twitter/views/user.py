""" user.py """
import tweepy
from django import forms
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django.template import loader
from requests.exceptions import HTTPError

from twitter.models import User


def user(request, id: int = None):
  """ view for twitter/users """
  template = loader.get_template('user/index.html')
  instance = None
  if id is not None:
    instance = get_object_or_404(User, id=id)

  error = ''
  form = NewUserForm(request.POST or None, instance=instance)
  if request.method == "POST":
    if form.is_valid():
      error = login_error(form)
      if error == "":
        form.save()
        return redirect('twitter:user')

  context = {
    'form': form,
    'title': 'Users',
    'users': User.objects.all(),
    'error': error,
    'id': id
  }
  return HttpResponse(template.render(context, request))

class NewUserForm(forms.ModelForm):
  """ Form to create a new user"""
  def __init__(self, *args, **kwargs):
    super(NewUserForm, self).__init__(*args, **kwargs)

  class Meta:
    model = User
    fields = ('username', 'api_key', 'api_secret', 'api_access_token', 'api_token_secret')

def login_error(form: NewUserForm) -> str:
  """ Checks whether user has valid login """
  api_key = form.data.get('api_key')
  api_secret = form.data.get('api_secret')
  api_access_token = form.data.get('api_access_token')
  api_token_secret = form.data.get('api_token_secret')
  auth = tweepy.OAuthHandler(api_key, api_secret)
  auth.set_access_token(api_access_token, api_token_secret)
  api = tweepy.API(auth)
  if not api.verify_credentials():
    return "Invalid twitter credentials"
  return ""
