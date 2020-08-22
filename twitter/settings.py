""" settings.py """
import json
import os

USER_SETTINGS = "twitter/settings.json"
DEFAULT_SETTINGS = "twitter/default-settings.json"

class SchedulerSettings:
  """ Settings for scheduler.py """
  def __init__(self, d):
    settings_d = d.get('Scheduler', {})

    # how long to sleep before checking new things to tweet
    self.sleep = settings_d.get("sleep")

    # the seconds offset to run a job.
    # e.g. 120 means a tweet can run +/- 120 seconds from schedule
    self.precision = settings_d.get("precision")

    # how long to sleep after failure
    self.sleep_failure = settings_d.get("sleep_failure")

class ManageSettings:
  """ Settings for manage.py """
  def __init__(self, d):
    settings_d = d.get('Manage', {})

    # how many old sent tweets to show in manage
    self.show_old = settings_d.get("show_old")

class FollowSettings:
  """ Settings for manage.py """
  def __init__(self, d):
    settings_d = d.get('Follow', {})

    # number of follow suggestions to generate
    self.num_suggestions = settings_d.get("num_suggestions")

    # number of days before unfollowing someone
    self.unfollow_default_days = settings_d.get("unfollow_default_days")

    # commas separated list of words to exclude when generating follow suggestions
    self.default_blacklist = settings_d.get("default_blacklist")

class GenerateSettings:
  """ Settings for manage.py """
  def __init__(self, d):
    settings_d = d.get('Generate', {})

    # number of  tweet suggestions to generate
    self.num_suggestions = settings_d.get("num_suggestions")

class NewsSettings:
  """ Settings for news.py """
  def __init__(self, d):
    settings_d = d.get('News', {})

    # number of  tweet suggestions to generate
    self.default_sources = settings_d.get("default_sources")

    self.default_topic = settings_d.get("default_topic")

class SettingsClass:
  """ class to hold all user settings """
  def __init__(self):
    settings_path = USER_SETTINGS if os.path.exists(USER_SETTINGS) else DEFAULT_SETTINGS
    with open(settings_path, "r") as f:
      self.inner = json.loads(f.read())
    self.scheduler = SchedulerSettings(self.inner)
    self.manage = ManageSettings(self.inner)
    self.follow = FollowSettings(self.inner)
    self.generate = GenerateSettings(self.inner)
    self.news = NewsSettings(self.inner)

settings = SettingsClass()
