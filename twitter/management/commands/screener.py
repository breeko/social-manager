"""screener.py"""
import collections
import csv
import os
from collections import namedtuple, OrderedDict
from time import sleep
from typing import List

import tweepy
from django.core.management.base import BaseCommand

from twitter.models import User
from twitter.utils.twitter_utils import get_api, get_botometer
from .screener_utils import flatten_dict, column_orderings

UserFilter = namedtuple("UserFilter", "min_friends max_friends min_followers max_followers")

def get_overlap(api: tweepy.API, name: str) -> float:
  friends = set()
  followers = set()
  for page in tweepy.Cursor(api.friends_ids, screen_name=name).pages():
    friends = friends | set(page)
    sleep(5)
  for page in tweepy.Cursor(api.followers_ids, screen_name=name).pages():
    followers = followers | set(page)
    sleep(5)
  score = len(followers.intersection(friends)) / len(followers)
  return score

def flatten(d, parent_key='', sep='_'):
  items = []
  for k, v in d.items():
    new_key = parent_key + sep + k if parent_key else k
    if isinstance(v, collections.MutableMapping):
      items.extend(flatten(v, new_key, sep=sep).items())
    else:
      items.append((new_key, v))
  return dict(items)


class MyStreamListener(tweepy.StreamListener):
  def __init__(self, out_path, user_filter: UserFilter, api, botometer):
    super().__init__(api)
    self._seen = set()
    self.botometer = botometer
    self.out_path = out_path
    self.user_filter = user_filter
    if os.path.exists(out_path):
      with open(out_path, "r") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=",")
        next(csv_reader)
        for row in csv_reader:
          self._seen.add(row[0])
    else:
      with open(out_path, "w") as csv_file:
        writer = csv.writer(csv_file)
        # botometer score of 0 means real, 1 is bot
        writer.writerow([
          "name", "friend_follower_overlap", "boto_english", "boto_universal",
          "boto_content", "boto_friend", "boto_network", "boto_sentiment", "boto_temporal", "boto_user"
        ] + column_orderings)

  def _get_boto_results(self, username: str):
    if self.botometer is None:
      return [""] * 8
    results = self.botometer.check_account(username)
    english = results["cap"]["english"]
    universal = results["cap"]["universal"]
    content = results["categories"]["content"]
    friend = results["categories"]["friend"]
    network = results["categories"]["network"]
    sentiment = results["categories"]["sentiment"]
    temporal = results["categories"]["temporal"]
    user = results["categories"]["user"]
    return [english, universal, content, friend, network, sentiment, temporal, user]
    
  def on_status(self, status):
    user = status.user
    name = user.screen_name
    if name not in self._seen and \
        user.followers_count >= self.user_filter.min_followers and \
        user.followers_count <= self.user_filter.max_followers and \
        user.friends_count >= self.user_filter.min_friends and \
        user.friends_count <= self.user_filter.max_friends:
      overlap = get_overlap(self.api, name)
      with open(self.out_path, "a+") as csv_file:
        writer = csv.writer(csv_file)
        boto_results = self._get_boto_results(user.screen_name)
        user_d = flatten_dict(user._json)
        user_results = [user_d.get(column, "N/A") for column in column_orderings]
        row = [name, overlap] + boto_results + user_results
        writer.writerow(row)
      self._seen.add(name)

  def on_error(self, status_code):
    if status_code == 420:
      # returning False in on_error disconnects the stream
      return False

def run(username: str, out_path: str, hashtags: List[str], user_filter: UserFilter):
  user = User.objects.get(username=username)
  api = get_api(user)
  botometer = get_botometer(user)
  stream_listener = MyStreamListener(out_path=out_path, user_filter=user_filter, api=api, botometer=botometer)

  while True:
    try:
      stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
      stream.filter(track=hashtags)
    except tweepy.error.TweepError:
      continue
    except (KeyboardInterrupt, SystemExit):
      return

class Command(BaseCommand):
  """ Screens hashtags and saves users locally """
  help = """Screens hashtags and saves users locally. You can set settings in settings.py """
  def add_arguments(self, parser):
    parser.add_argument("username", help="Username")
    parser.add_argument("hashtags", type=str, nargs="+", help="Hashtags to follow")
    parser.add_argument("-o", "--out", dest="out_path", default="screener.csv", help="Output path")
    parser.add_argument("--min-friends", type=int, dest="min_friends", default=100, help="Min number of friends")
    parser.add_argument("--max-friends", type=int, dest="max_friends", default=1000, help="Max number of friends")
    parser.add_argument("--min-followers", type=int, dest="min_followers", default=100, help="Min number of followers")
    parser.add_argument("--max-followers", type=int, dest="max_followers", default=1000, help="Max number of followers")
  def handle(self, *args, **options):
    username = options["username"]
    hashtags = options["hashtags"]
    out_path = options["out_path"]
    user_filter = UserFilter(
      min_friends=options["min_friends"],
      max_friends=options["max_friends"],
      min_followers=options["min_followers"],
      max_followers=options["max_followers"]
    )
    run(username=username, out_path=out_path, hashtags=hashtags, user_filter=user_filter)
