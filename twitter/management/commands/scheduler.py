""" tweetscheduler.py """

import csv
import logging
from datetime import datetime, timedelta
from time import sleep
from typing import List

import pytz
from croniter import croniter
from django.core.management.base import BaseCommand
from django.db.utils import OperationalError
from django.utils import timezone
from tweepy.error import TweepError

from social.settings import TIME_ZONE
from twitter.models import AutoFollow, Follow, Tweet
from twitter.settings import settings
from twitter.utils.date_utils import format_date, randomize_date
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

def get_follows(auto_follow: AutoFollow) -> List[Follow]:
  """ Returns list of follows based on AutoFollow """
  already_followed = {f.username for f in Follow.objects.all()}
  follows = []
  cur_ct = 0
  with open(auto_follow.path, "r") as csv_file:
    csv_reader = csv.DictReader(csv_file)
    for row in csv_reader:
      name = row.get("screen_name")
      friend_follower_overlap = row.get("friend_follower_overlap")
      if name is None or friend_follower_overlap is None or cur_ct >= auto_follow.count:
        break
      if float(friend_follower_overlap) >= auto_follow.min_friend_follower_overlap and \
        name not in already_followed:
        follow_date = randomize_date(hours=auto_follow.over_hours)
        unfollow_date = None
        if auto_follow.unfollow_days is not None:
          unfollow_date = randomize_date(hours=auto_follow.unfollow_days) + \
            timedelta(days=settings.follow.unfollow_default_days)
        follow = Follow(user=auto_follow.user, username=name, follow=follow_date, unfollow=unfollow_date)
        follows.append(follow)
        already_followed.add(name)
        cur_ct += 1
  return follows

def should_run(schedule: str, now: datetime):
  """ Returns boolean indicating whether schedule has elapsed since last sleep """
  tz = pytz.timezone(TIME_ZONE)
  local_date = tz.localize(datetime.now()) - timedelta(seconds=settings.scheduler.sleep)
  next_date = croniter(schedule, local_date).get_next(datetime)
  return next_date <= now

def process_auto_follow(now: datetime, debug: bool):
  """ Collects all auto-follows and creates follow objects"""
  auto_follows = [af for af in AutoFollow.objects.all() if should_run(af.schedule, now)]
  for af in auto_follows:
    to_follow = get_follows(af)
    # if not debug:
    Follow.objects.bulk_create(to_follow)
    logging.info("[%s]: auto-followed %s acounts", af.user.username, len(to_follow))

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
      try:
        process_auto_follow(now, debug)
      except Exception as e:
        logging.error("Failure to auto: %s", e)

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
