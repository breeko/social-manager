# social-manager

Django app to manage social media locally.

Schedule tweets and automatically generate tweets. Multiple account support, just load your api keys.

```
> echo "SECRET_KEY=${openssl rand -base64 50}" > secrets.py 
> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> python manage.py migrate

// you need to run two processes, one for the scheduler and the other for the server
> screen -A social-manager-scheduler
> python manage.py tweetscheduler

// detach screen ctrl+a d
> screen -A social-manager-server
> python manage.py runserver
// detach screen ctrl+a d
```

Platforms Supported
- Twitter

TODO:
- Add multi-media support
- Add retweets
- Ability to run arbitrary scripts to generate content
- Add Instagram

