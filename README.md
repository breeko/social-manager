# social-manager

Django app to manage social media locally.

Schedule tweets and automatically generate tweets. Multiple account support, just load your api keys.

```
# create a secret key and put into secrets.json (see secrets-example.json)

> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> python manage.py migrate

// you need to run two processes, one for the scheduler and the other for the server
// scheduler actually does the tweeting, server allows you to interact

> screen -A social-manager-scheduler
> source venv/bin/activate
> python manage.py tweetscheduler

// detach screen ctrl+a d
> screen -A social-manager-server
> source venv/bin/activate
> python manage.py runserver
// detach screen ctrl+a d
```

### Using social manager

- Go to User and add your api credentials from twitter. 
  - It'll verify whether they're correct
- Create and schedule messages using Create tab
- Generate and schdule messages using Generate tab
  - Generate allows you to see trends and give you suggested tweets based on a keyword
- Manage messages using Manage tab
- Follow allows you to find, filter and follow users and optionally unfollow them after a period of time

### Customize
twitter/settings.py
- `TWEET_SCHEDULE_OFFSET` = 120
  - the seconds offset to run a job. e.g. 120 means a tweet can run +/- 120 seconds from schedule
- `TWEET_SCHEDULE_SLEEP` = 5
  - how long to sleep before checking new things to tweet
- `TWEET_SHOW_OLD` = 5
  - how many old sent tweets to show in manage
- `UNFOLLOW_DEFAULT_DAYS` = None
  - number of days before unfollowing someone
  - NOTE: following and unfollowing users is against Twitter's TOS and will get you suspended
- `NUM_FOLLOW_SUGGESTIONS` = 50
  - number of people you want to recommend following
- `NUM_GENERATE_SUGGESTIONS` = 2
  - number of suggestions to generate
- `LAST_TWEET_DAYS` = 7
  - when finding users, filter on users that have tweeted in LAST_TWEET_DAYS days
- `DEFAULT_NEWS_SOURCES` = "news.ycombinator.com, techcrunch.com, nytimes.com"
  - the default news sources to search

### Platforms Supported
- Twitter

## TODO:
- Add multi-media support
- Add retweets
- Ability to run arbitrary scripts to generate content
- Add Instagram
