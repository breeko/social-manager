from twitter.models import User, Tweet, Follow
from time import sleep
from django.utils import timezone
from twitter.settings import TWEET_SCHEDULE_OFFSET, TWEET_SCHEDULE_SLEEP
from django.core.management.base import BaseCommand, CommandError
import logging
from twitter.utils.twitter_utils import get_api

logging.basicConfig(
  filename='tweetscheduler.log',
  filemode='a',
  format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
  datefmt='%H:%M:%S',
  level=logging.DEBUG
)

def process_tweet(tweet: Tweet):
  api = get_api(tweet.user)
  api.update_status(tweet.body)
  tweet.sent = timezone.now()
  tweet.save(update_fields=["sent"])
  logging.info(f"[{tweet.user.username}]: {tweet.body}")

def process_follow(follow: Follow):
  api = get_api(follow.user)
  api.create_friendship(follow.username)
  follow.followed = timezone.now()
  follow.save(update_fields=['followed'])
  logging.info(f"[{follow.user.username}]: friended {follow.username}")

def process_unfollow(follow: Follow):
  api = get_api(follow.user)
  api.destroy_friendship(follow.username)
  follow.unfollowed = timezone.now()
  follow.save(update_fields=['unfollowed'])
  logging.info(f"[{follow.user.username}]: unfriended {follow.username}")

class Command(BaseCommand):
  help = f"""
    Runs tweet schedule. You can set settings in settings.py.

    TWEET_SCHEDULE_OFFSET={TWEET_SCHEDULE_OFFSET}
    TWEET_SCHEDULE_SLEEP={TWEET_SCHEDULE_SLEEP}
  """
  def handle(self, *args, **options):
    while True:
      handle_tweet()
      handle_follow()
      sleep(TWEET_SCHEDULE_SLEEP)


def handle_tweet():
  offset = timezone.timedelta(seconds=TWEET_SCHEDULE_OFFSET)
  now = timezone.now()
  start = now - offset
  end = now + offset
  tweets = Tweet.objects.filter(scheduled__gte=start, scheduled__lte=end, sent__isnull=True)
  all_tweets = Tweet.objects.all()
  for tweet in tweets:
    process_tweet(tweet)
      

def handle_follow():
  now = timezone.now()
  follows = Follow.objects.filter(follow__lte=now, followed__isnull=True)
  unfollows = Follow.objects.filter(unfollow__lte=now, unfollowed__isnull=True)
  for f in follows:
    process_follow(f)

  for u in unfollows:
    process_unfollow(u)
  
  
