""" users.py """
import tweepy
from django import forms
from django.http import HttpResponse
from django.shortcuts import render
from django.template import loader

from twitter.models import User


def users(request):
  """ view for twitter/users """
  template = loader.get_template('users/index.html')
  form = NewUserForm(request.POST)

  error = ''
  if request.method == "POST":
    if form.is_valid() and login_valid(form):
      form.save(commit=True)
      form = NewUserForm()
    else:
      error = 'Invalid credentials'
  else:
    form = NewUserForm()

  usernames = [u.username for u in User.objects.all()]
  context = {
    'form': form,
    'title': 'Users',
    'users': usernames,
    'error': error
  }
  return HttpResponse(template.render(context, request))

class NewUserForm(forms.ModelForm):
  """ Form to create a new user"""
  class Meta:
    model = User
    fields = ('username', 'api_key', 'api_secret', 'api_access_token', 'api_token_secret',)
    widgets = {
      'api_key': forms.PasswordInput(),
      'api_secret': forms.PasswordInput(),
      'api_access_token': forms.PasswordInput(),
      'api_token_secret': forms.PasswordInput(),
    }

def login_valid(form: NewUserForm) -> bool:
  """ Checks whether user has valid login """
  api_key = form.data.get('api_key')
  api_secret = form.data.get('api_secret')
  api_access_token = form.data.get('api_access_token')
  api_token_secret = form.data.get('api_token_secret')
  auth = tweepy.OAuthHandler(api_key, api_secret)
  auth.set_access_token(api_access_token, api_token_secret)
  api = tweepy.API(auth)
  valid = api.verify_credentials() != False
  return valid
