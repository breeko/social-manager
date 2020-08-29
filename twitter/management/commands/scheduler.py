""" tweetscheduler.py """

import logging
from datetime import datetime, timedelta
from sqlite3 import OperationalError
from time import sleep

from django.core.management.base import BaseCommand
from django.utils import timezone
from tweepy.error import TweepError

from twitter.models import Follow, Tweet
from twitter.settings import settings
from twitter.utils.twitter_utils import get_api

logging.basicConfig(
  filename='logs/scheduler/scheduler.log',
  filemode='a',
  format='%(asctime)s %(levelname)s %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  level=logging.INFO
)

def process_tweet(tweet: Tweet, debug: bool):
  """ Processes user tweets """
  if not debug:
    api = get_api(tweet.user)
    api.update_status(tweet.body)
  tweet.sent = timezone.localtime()
  tweet.save(update_fields=["sent"])
  logging.info("[%s]: tweeted %s", tweet.user.username, tweet.body)

def process_follow(follow: Follow, debug: bool):
  """ Processes user follows """
  if not debug:
    api = get_api(follow.user)
    api.create_friendship(follow.username)
  follow.followed = timezone.localtime()
  follow.save(update_fields=['followed'])
  logging.info("[%s]: followed %s", follow.user.username, follow.username)

def process_unfollow(follow: Follow, debug: bool):
  """ Processes user unfollows """
  if not debug:
    api = get_api(follow.user)
    api.destroy_friendship(follow.username)
  follow.unfollowed = timezone.localtime()
  follow.save(update_fields=['unfollowed'])
  logging.info("[%s]: unfollowed %s", follow.user.username, follow.username)

class Command(BaseCommand):
  """ Runs tweet schedule """
  help = """Runs tweet schedule. You can set settings in settings.py """
  def add_arguments(self, parser):
    # Named (optional) arguments
    parser.add_argument(
      '--debug',
      action='store_true',
      help="Run in debug mode, don't actually tweet, follow or unfollow",
    )
  def handle(self, *args, **options):
    debug = options.get('debug', False)
    tweet_sleep_until = datetime.min
    follow_sleep_until = datetime.min
    while True:
      now = datetime.now()
      if now > tweet_sleep_until:
        try:
          handle_tweet(debug)
        except TweepError as err:
          logging.error("Failure to tweet: %s", err)
          tweet_sleep_until = now + timedelta(seconds=settings.scheduler.sleep_failure)
        except OperationalError:
          continue # database locked
      if now > follow_sleep_until:
        try:
          handle_follow(debug)
        except TweepError as err:
          logging.error("Failure to tweet: %s", err)
          follow_sleep_until = now + timedelta(seconds=settings.scheduler.sleep_failure)
        except OperationalError:
          continue # database locked

      sleep(settings.scheduler.sleep)

def handle_tweet(debug: bool):
  """ Handles user tweets """
  offset = timezone.timedelta(seconds=settings.scheduler.precision)
  now = timezone.localtime()
  start = now - offset
  end = now + offset
  tweets = Tweet.objects.filter(scheduled__gte=start, scheduled__lte=end, sent__isnull=True)
  for tweet in tweets:
    process_tweet(tweet, debug)

def handle_follow(debug: bool):
  """ Handles user follows """
  now = timezone.localtime()
  follows = Follow.objects.filter(follow__lte=now, followed__isnull=True)
  unfollows = Follow.objects.filter(unfollow__lte=now, unfollowed__isnull=True)
  for follow in follows:
    process_follow(follow, debug)

  for unfollow in unfollows:
    process_unfollow(unfollow, debug)
