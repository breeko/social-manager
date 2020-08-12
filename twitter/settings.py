""" settings.py """

class TweetSchedulerSettings:
  """ Settings for tweetscheduler.py """
  # how long to sleep before checking new things to tweet
  SLEEP = 5

  # the seconds offset to run a job. e.g. 120 means a tweet can run +/- 120 seconds from schedule
  SCHEDULE_PRECISION = 120

  # how long to sleep after failure
  SLEEP_FAILURE = 60 * 60 * 2

class ManageSettings:
  """ Settings for manage.py """

  # how many old sent tweets to show in manage
  SHOW_OLD = 5

class FollowSettings:
  """ Settings for follow.py """

  # number of days before unfollowing someone
  UNFOLLOW_DEFAULT_DAYS = 5

  # number of follow suggestions to generate
  NUM_FOLLOW_SUGGESTIONS = 50

  # default filter for users with this many days since last tweet
  LAST_TWEET_DAYS = 7

class GenerateSettings:
  """ Settings for generate.py """
  # number of  tweet suggestions to generate
  NUM_GENERATE_SUGGESTIONS = 2


class NewsSettings:
  DEFAULT_NEWS_SOURCES = "news.ycombinator.com, techcrunch.com, nytimes.com"
  
  DEFAULT_TOPIC = "tech"
