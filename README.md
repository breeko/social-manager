# social-manager

Django app to manage social media locally.

Schedule tweets, follows and unfollows. Find accounts to follow. Multiple account support, just load your api keys.

```
# create a secret key and put into secrets.json (see secrets-example.json)

> python3 -m venv venv
> source venv/bin/activate
> pip install -r requirements.txt
> python manage.py migrate

// you need to run two processes, one for the scheduler and the other for the server
// scheduler does the tweeting, server allows you to interact

> screen -A social-scheduler
> source venv/bin/activate
> python manage.py scheduler

// detach screen ctrl + a d
> screen -A social-server
> source venv/bin/activate
> python manage.py runserver
// detach screen ctrl + a d
```

`Screener` function lets you screen tweets based on geography and output user information. You can then user this information to find people to follow.

## Using social manager

- Go to `User` and add your api credentials from twitter. 
  - It'll verify whether they're correct
- `Create` and schedule messages
- `Manage` scheduled messages and follows/unfollows
- `Follow` allows you to schedule bulk follows/unfollows
  - NOTE: following then unfollowing large number of users, churning, is against twitter TOS
- `News` allows you to find, filter and schedule posting links based on news sources
- `Logs` Shows you logs (e.g. failure to send tweets, api limits, etc)

## Using screener

Social screener screens tweets based on a geography.

To run use command:

`python manage.py screener [username] [locations]+`

e.g. below will use credentials from `my_bot` and get information on all users tweeting from New York or California

`python manage.py my_bot "California" "New York"`

This will append users that tweet and their attribues to `screener.csv`

Optional arguments are below

```
-o, --out, (default="screener.csv"): Output path
--min-friends (default=100): Min number of friends
--max-friends (default 1000): Max number of friends
--min-followers (default=100): Min number of followers
--max-followers (default=1000): Max number of followers
```
e.g. 

`python manage.py my_bot "New York" --min-friends 1000 --max-friends 10000 --out ny.csv`

While running screener, you will almost certainly hit your twitter api limits, in which case the script will sleep until the api limit is reset (every 15 minutes).

The output contains 100+ columns of user information (e.g. description, last tweet, whether they're using a default profile picture). It also includes `friend_follower_overlap`, which tells you the percentage of followers they follow as well. This is a good predictor of liklihood of followback.

## Screenshots
![users](static/screenshots/user.png?raw=true "User")

![create](static/screenshots/create.png?raw=true "Create")

![follow](static/screenshots/follow.png?raw=true "Follow")

![manage](static/screenshots/manage.png?raw=true "Manage")

![news](static/screenshots/news.png?raw=true "News")


## Customize
Customize settings and defaults at twitter/settings.json

## Platforms Supported
- Twitter

## TODO:
- Add multi-media support
- Add retweets
- Ability to run arbitrary scripts to generate content
- Add Instagram
