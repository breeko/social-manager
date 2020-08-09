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
- Manage message using Manage tab

### Customize
- social/settings.py has two pertinent fields TWEET_SCHEDULE_OFFSET and TWEET_SCHEDULE_SLEEP
  - TWEET_SCHEDULE_OFFSET is the seconds offset to run a job.
    - e.g. 120 means a tweet can run +/- 120 seconds from schedule
  - TWEET_SCHEDULE_SLEEP is the amount of time it sleeps before checking the database again (in seconds)


### Platforms Supported
- Twitter

## TODO:
- Add multi-media support
- Add retweets
- Ability to run arbitrary scripts to generate content
- Add Instagram
