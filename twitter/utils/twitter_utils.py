""" twitter_utils.py"""
from typing import Callable, List

import tweepy
from botometer import Botometer
from tweepy.api import API

from twitter.utils.parse_utils import build_expr

def get_api(user: 'User') -> API:
  """ Returns an api object based on user credentials """
  auth = tweepy.OAuthHandler(user.api_key, user.api_secret)
  auth.set_access_token(user.api_access_token, user.api_token_secret)
  api = tweepy.API(auth, wait_on_rate_limit=True, wait_on_rate_limit_notify=True, compression=True)
  return api

def get_botometer(user: 'User') -> Botometer:
  """ Returns an api object based on user credentials """
  if user.rapidapi_key is None:
    return None
  botometer = Botometer(
    consumer_key=user.api_key,
    consumer_secret=user.api_secret,
    access_token=user.api_access_token,
    access_token_secret=user.api_token_secret,
    rapidapi_key=user.rapidapi_key
  )
  return botometer

def get_trends(user: 'User', geo_code: int = 23424977) -> List[str]:
  """ Returns trends in a given geo-code (default US) """
  api = get_api(user)
  trends = api.trends_available()
  trends = api.trends_place(geo_code)
  trends_names = [n.get('name') for n in trends[0]['trends']]
  return trends_names

def get_suggestions(
    user: 'User',
    hashtag: str,
    valid_user: Callable[['User'], bool],
    since: str,
    max_suggestions: int
  ) -> List[tweepy.models.User]:
  """ Returns friend suggestions based on current friends
    Input:
      user [User]: user to get api login
      hashtag [str]: hashtag to search
      valid_user [User => bool]: function to filter valid users
      max_suggestions [int]: maximum number of suggestions to return
    Output:
      users [List[tweepy.model.User]]: list of users that match valid_user
  """
  api = get_api(user)
  suggestions = []
  seen = set()
  max_iters = 5000

  for tweet in tweepy.Cursor(api.search, q=hashtag, lang="en", since=since).items():
    if tweet.user.screen_name not in seen and valid_user(tweet.user):
      suggestions.append(tweet.user)
    seen.add(tweet.user.screen_name)
    if len(suggestions) >= max_suggestions or len(seen) > max_iters:
      break

  return suggestions

def create_valid_user(blacklist: str, expressions: List[str]) -> bool:
  """ Returns a function that takes a user and returns whether the user is valid
    e.g. f('bot', ['friends_count > 100', 'followers_count >= 200'])
  """
  built_expressions = []
  for expression in expressions:
    built = build_expr(expression)
    built_expressions.append(built)

  valid = lambda u: all([expr(u) for expr in built_expressions])

  def valid_user(user: 'User') -> bool:
    return \
      (blacklist == '' or not any([w for w in blacklist.split(",") if w.lower() in user.description.lower()])) \
        and valid(user)
  return valid_user
