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
> python manage.py scheduler

// detach screen ctrl+a d
> screen -A social-manager-server
> source venv/bin/activate
> python manage.py runserver
// detach screen ctrl+a d
```

## Using social manager

- Go to `User` and add your api credentials from twitter. 
  - It'll verify whether they're correct
- `Create` and schedule messages
- `Generate` and schdule messages
  - Generate allows you to see trends and give you suggested tweets based on a keyword or phrase
- `Manage` scheduled messages using
- `Follow` allows you to find, filter and schedule follows and optionally unfollows after a period of time
  - NOTE: following then unfollowing large number of users, churning, is against twitter TOS
- `News` allows you to find, filter and schedule posting links based on news sources

## Screenshots
![users](static/screenshots/users.png?raw=true "Users")

![create](static/screenshots/create.png?raw=true "Create")

![follow](static/screenshots/follow.png?raw=true "Follow")

![manage](static/screenshots/manage.png?raw=true "Manage")

![generate](static/screenshots/generate.png?raw=true "Generate")

![news](static/screenshots/news.png?raw=true "news")


## Customize
Customize settings and defaults at twitter/settings.py

## Platforms Supported
- Twitter

## TODO:
- Add multi-media support
- Add retweets
- Ability to run arbitrary scripts to generate content
- Add Instagram
