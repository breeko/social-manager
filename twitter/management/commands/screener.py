"""screener.py"""
import csv
import os
from collections import namedtuple

import geocoder
import tweepy
from django.core.management.base import BaseCommand
from urllib3.exceptions import ProtocolError

from twitter.models import User
from twitter.utils.twitter_utils import get_api, get_botometer

from .screener_utils import column_orderings, flatten_dict, get_overlap

UserFilter = namedtuple("UserFilter", "min_friends max_friends min_followers max_followers")

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
    name = status.user.screen_name
    if name not in self._seen and \
        status.user.followers_count >= self.user_filter.min_followers and \
        status.user.followers_count <= self.user_filter.max_followers and \
        status.user.friends_count >= self.user_filter.min_friends and \
        status.user.friends_count <= self.user_filter.max_friends:
      overlap = get_overlap(self.api, name)
      user = self.api.get_user(name)
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
      return True

class Command(BaseCommand):
  """ Screens hashtags and saves users locally """
  help = """Screens hashtags and saves users locally. You can set settings in settings.py """

  def add_arguments(self, parser):
    parser.add_argument("username", help="Username")
    parser.add_argument("locations", type=str, nargs="+", help="Locations to filter")
    parser.add_argument("-o", "--out", dest="out_path", default="screener.csv", help="Output path")
    parser.add_argument("--min-friends", type=int, dest="min_friends", default=100, help="Min number of friends")
    parser.add_argument("--max-friends", type=int, dest="max_friends", default=1000, help="Max number of friends")
    parser.add_argument("--min-followers", type=int, dest="min_followers", default=100, help="Min number of followers")
    parser.add_argument("--max-followers", type=int, dest="max_followers", default=1000, help="Max number of followers")

  def handle(self, *args, **options):
    username = options["username"]
    locations = options["locations"]
    out_path = options["out_path"]
    user_filter = UserFilter(
      min_friends=options["min_friends"],
      max_friends=options["max_friends"],
      min_followers=options["min_followers"],
      max_followers=options["max_followers"]
    )
    user = User.objects.get(username=username)
    api = get_api(user)
    botometer = get_botometer(user)
    stream_listener = MyStreamListener(out_path=out_path, user_filter=user_filter, api=api, botometer=botometer)

    coords = []

    for location in locations:
      res = geocoder.osm(location).json
      if res:
        # [long, lat]
        coord = res['bbox']['southwest'][::-1] + res['bbox']['northeast'][::-1]
        coords.extend(coord)
    while True:
      try:
        stream = tweepy.Stream(auth=api.auth, listener=stream_listener)
        stream.filter(locations=coords)
      except (ProtocolError, tweepy.error.TweepError):
        continue
      except (KeyboardInterrupt, SystemExit):
        return
