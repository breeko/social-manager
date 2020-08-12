import json
import re
from datetime import datetime
from random import shuffle
from typing import Callable, List

import requests
import tweepy
from bs4 import BeautifulSoup
from requests.utils import quote
from tweepy.api import API

from twitter.models import User

MODEL_CHOICES = (
  ('gpt2', 'gpt2'),
  ('gpt2-xl', 'gpt2-xl'),
  ('gpt2-large', 'gpt2-large'),
  ('gpt2-medium', 'gpt2-medium'),
  ('html','html'),
)

def generate_tweet(phrase: str, model: str) -> str:
  """ Generates a tweet based on a phrase and model """
  if model == "html":
    return generate_html(phrase)
  elif model.startswith('gpt2'):
    return generate_hugging_face(phrase, model)
  else:
    return ''

def generate_html(phrase: str):
  url = f"https://thoughts.sushant-kumar.com/{quote(phrase)}"
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "html.parser")
  out = soup.blockquote.text.replace("\n","")[1:-1]
  return out

def generate_hugging_face(phrase: str, model: str) -> str:
  """ valid models: gpt2, gpt2-xl, gpt2-large, gpt2-medium"""
  headers = {
      'Authorization': 'Bearer YOUR_ORG_OR_USER_API_TOKEN',
      'Content-Type': 'application/json',
  }
  data = f'"{phrase}"'
  raw = requests.post(f'https://api-inference.huggingface.co/models/{model}', headers=headers, data=data)
  try:
    response = json.loads(raw.text)
    return response[0].get('generated_text')
  except:
    return ""


def get_api(user: User) -> API:
  auth = tweepy.OAuthHandler(user.api_key, user.api_secret)
  auth.set_access_token(user.api_access_token, user.api_token_secret)
  api = tweepy.API(auth)
  return api

def get_trends(user: User) -> List[str]:
  api = get_api(user)
  US_CODE = 23424977
  trends = api.trends_available()
  [t for t in trends if t['name'] == 'United States']
  trends = api.trends_place(US_CODE)
  trends_names = [n.get('name') for n in trends[0]['trends']]
  return trends_names

def chunks(lst, n):
  """Yield successive n-sized chunks from lst."""
  for i in range(0, len(lst), n):
      yield lst[i:i + n]

def get_suggestions(user: User, valid_user: Callable[[User], bool], max_suggestions: int) -> List[tweepy.models.User]:
  """ Returns friend suggestions based on current friends
    Input:
      user [User]: user to get api login
      valid_user [User => bool]: function to filter valid users
      max_suggestions [int]: maximum number of suggestions to return
    Output:
      users [List[tweepy.model.User]]: list of users that match valid_user
  """
  api = get_api(user)
  suggestions = []
  friends = api.me().friends(count=200)
  shuffle(friends)
  for friend in friends:
    followers = api.followers_ids(friend.id) # returns 5000
    shuffle(followers)
    for chunk in chunks(followers, 100):
      candidates = api.lookup_users(user_ids=chunk)
      for candidate in candidates:
        if valid_user(candidate):
          suggestions.append(candidate)
          if len(suggestions) >= max_suggestions:
            return suggestions
  return suggestions



def create_valid_user(
  followers_max: str,
  followers_min: str,
  friends_max: str,
  friends_min: str,
  followers_friend_ratio_min: str,
  followers_friend_ratio_max: str,
  last_tweet: str
):
  def valid_user(user: User):
    return \
      (followers_min == '' or user.followers_count >= int(followers_min)) and \
      (followers_max == '' or user.followers_count <= int(followers_max)) and \
      (friends_min == '' or user.friends_count >= int(friends_min)) and \
      (friends_max == '' or user.friends_count <= int(friends_max)) and \
      (followers_friend_ratio_min == '' or user.followers_count / user.friends_count >= float(followers_friend_ratio_min)) and \
      (followers_friend_ratio_max == '' or user.followers_count / user.friends_count <= float(followers_friend_ratio_max)) and \
      (last_tweet == '' or get_last_tweet(user) >= parse_date(last_tweet))
  return valid_user

def parse_date(d: str) -> datetime:
  return datetime.strptime(d, "%Y-%m-%d")

def get_last_tweet(user: User) -> datetime:
  try:
    return user.status.created_at
  except:
    return datetime.min
