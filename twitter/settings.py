
# the seconds offset to run a job. e.g. 120 means a tweet can run +/- 120 seconds from schedule
TWEET_SCHEDULE_OFFSET = 120

### server settings

# how long to sleep before checking new things to tweet
TWEET_SCHEDULE_SLEEP = 5


### manage settings
# how many old sent tweets to show in manage
TWEET_SHOW_OLD = 5


### follow settings
# number of days before unfollowing someone
UNFOLLOW_DEFAULT_DAYS = 5

# number of follow suggestions to generate
NUM_FOLLOW_SUGGESTIONS = 50


### generate settings
# number of  tweet suggestions to generate
NUM_GENERATE_SUGGESTIONS = 2

# default filter for users with this many days since last tweet
LAST_TWEET_DAYS = 7

### news settings
DEFAULT_NEWS_SOURCES = "news.ycombinator.com, techcrunch.com, nytimes.com"
