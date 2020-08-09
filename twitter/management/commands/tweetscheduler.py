from twitter.models import User, Tweet
from time import sleep
from django.utils import timezone
from social.settings import TWEET_SCHEDULE_OFFSET, TWEET_SCHEDULE_SLEEP
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
  api = get_api(tweet.user_id)
  api.update_status(tweet.body)
  tweet.sent = timezone.now()
  tweet.save(update_fields=["sent"])
  logging.info(f"[{tweet.user_id.username}]: {tweet.body}")

class Command(BaseCommand):
  help = f"""
    Runs tweet schedule. You can set settings in settings.py.

    TWEET_SCHEDULE_OFFSET={TWEET_SCHEDULE_OFFSET}
    TWEET_SCHEDULE_SLEEP={TWEET_SCHEDULE_SLEEP}
  """
  def handle(self, *args, **options):
    offset = timezone.timedelta(seconds=TWEET_SCHEDULE_OFFSET)
    while True:
      now = timezone.now()
      start = now - offset
      end = now + offset
      tweets = Tweet.objects.filter(scheduled__gte=start, scheduled__lte=end, sent__isnull=True)
      all_tweets = Tweet.objects.all()
      for tweet in tweets:
        process_tweet(tweet)
      sleep(TWEET_SCHEDULE_SLEEP)