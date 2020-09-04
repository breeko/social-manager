""" tweetscheduler.py """

import logging
from datetime import datetime, timedelta
from django.db.utils import OperationalError
from time import sleep

from django.core.management.base import BaseCommand
from django.utils import timezone
from tweepy.error import TweepError

from twitter.models import Follow, Tweet
from twitter.settings import settings
from twitter.utils.date_utils import format_date
from twitter.utils.twitter_utils import get_api

LOGGING_PATH = "logs/scheduler/scheduler.log"
STATUS_PATH = "logs/scheduler/status.log"

logging.basicConfig(
  filename=LOGGING_PATH,
  filemode='a',
  format='%(asctime)s %(levelname)s %(message)s',
  datefmt='%Y-%m-%d %H:%M:%S',
  level=logging.INFO
)

def user_exists(api, user):
  try:
    api.get_user(user)
    return True
  except TweepError:
    return False

def write_last_run(now: datetime):
  with open(STATUS_PATH, "w") as f:
    f.write(format_date(now))

def process_tweet(tweet: Tweet, now: datetime, debug: bool):
  """ Processes user tweets """
  if not debug:
    api = get_api(tweet.user)
    api.update_status(tweet.body)
  tweet.sent = now
  tweet.save(update_fields=["sent"])
  logging.info("[%s]: tweeted %s", tweet.user.username, tweet.body)

def process_follow(follow: Follow, now: datetime, debug: bool):
  """ Processes user follows """
  if not debug:
    api = get_api(follow.user)
    if user_exists(api, follow.username):
      api.create_friendship(screen_name=follow.username)
  follow.followed = now
  follow.save(update_fields=['followed'])
  logging.info("[%s]: followed %s", follow.user.username, follow.username)

def process_unfollow(follow: Follow, now: datetime, debug: bool):
  """ Processes user unfollows """
  if not debug:
    api = get_api(follow.user)
    if user_exists(api, follow.username):
      api.destroy_friendship(screen_name=follow.username)
  follow.unfollowed = now
  follow.save(update_fields=['unfollowed'])
  logging.info("[%s]: unfollowed %s", follow.user.username, follow.username)

class Command(BaseCommand):
  """ Runs tweet schedule """
  help = """Runs tweet schedule. You can set settings in settings.py """
  def add_arguments(self, parser):
    parser.add_argument(
      '--debug',
      action='store_true',
      help="Run in debug mode, don't actually tweet, follow or unfollow",
    )

  def handle(self, *args, **options):
    debug = options.get('debug', False)
    tweet_sleep_until = None
    follow_sleep_until = None
    while True:
      now = timezone.now()
      write_last_run(timezone.localtime())
      if tweet_sleep_until is None or now > tweet_sleep_until:
        try:
          handle_tweet(now, debug)
        except TweepError as err:
          logging.error("Failure to tweet: %s", err)
          tweet_sleep_until = now + timedelta(seconds=settings.scheduler.sleep_failure)
        except OperationalError:
          continue # database locked
      if follow_sleep_until is None or now > follow_sleep_until:
        try:
          handle_follow(now, debug)
        except TweepError as err:
          logging.error("Failure to follow: %s", err)
          follow_sleep_until = now + timedelta(seconds=settings.scheduler.sleep_failure)
        except OperationalError:
          continue # database locked

      sleep(settings.scheduler.sleep)

def handle_tweet(now: datetime, debug: bool):
  """ Handles user tweets """
  offset = timedelta(seconds=settings.scheduler.precision)
  start = now - offset
  end = now + offset
  tweets = Tweet.objects.filter(scheduled__range=(start, end), sent__isnull=True)
  for tweet in tweets:
    process_tweet(tweet, now, debug)

def handle_follow(now: datetime, debug: bool):
  """ Handles user follows """
  follows = Follow.objects.filter(follow__lte=now, followed__isnull=True)
  unfollows = Follow.objects.filter(unfollow__lte=now, unfollowed__isnull=True)
  for follow in follows:
    process_follow(follow, now, debug)

  for unfollow in unfollows:
    process_unfollow(unfollow, now, debug)
