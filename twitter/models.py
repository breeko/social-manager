""" models.py """

import csv
import os

from croniter import croniter
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.translation import gettext_lazy as _

from twitter.settings import settings


def validate_schedule(value: str):
  """ Validates whether schedule is valid """
  if not croniter.is_valid(value):
    raise ValidationError(
      _('%(value)s is not a valid crontab schedule'),
      params={'value': value},
    )

def validate_path(value: str):
  """ Validates whether a path exists """
  if not os.path.exists(value):
    raise ValidationError(
      _("%(value)s path doesn't exist"),
      params={'value': value},
    )
  elif not value.lower().endswith('.csv'):
    raise ValidationError(
      _('%(value)s must be a csv'),
      params={'value': value},
    )
  with open(value, "r") as csv_file:
    csv_reader = csv.reader(csv_file, delimiter=",")
    columns = next(csv_reader, [])
    if "name" not in columns or "friend_follower_overlap" not in columns:
      raise ValidationError(
        _('Invalid csv file. Must contain "name" and "friend_follower_overlap" columns. ' +
        'Columns found: %(value)s'),
        params={'value': ",".join(columns)}
      )

class User(models.Model):
  """ Model for user used to store credentials """
  id = models.AutoField(primary_key=True)
  username = models.CharField(max_length=80, unique=True, null=False)
  api_key = models.CharField(max_length=80, unique=True, null=False)
  api_secret = models.CharField(max_length=80, unique=True, null=False)
  api_access_token = models.CharField(max_length=80, unique=True, null=False)
  api_token_secret = models.CharField(max_length=80, unique=True, null=False)

  def __str__(self):
    return self.username

class Tweet(models.Model):
  """ Model for tweet used to store and schedule tweets made """
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  body = models.CharField(max_length=240, null=False)
  scheduled = models.DateTimeField('date scheduled', null=True, blank=True)
  sent = models.DateTimeField('date sent', null=True, blank=True)

  def __str__(self):
    return f'<Tweet {self.id} {self.body}>'

class Follow(models.Model):
  """ Model for tweet used to store and schedule follows made """
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  username = models.CharField(max_length=240, null=False)
  follow = models.DateTimeField('date to follow', null=True, blank=True)
  unfollow = models.DateTimeField('date to unfollow', null=True, blank=True)
  followed = models.DateTimeField('date did follow', null=True, blank=True)
  unfollowed = models.DateTimeField('date did unfollow', null=True, blank=True)

  def __str__(self):
    return f'<Follow {self.username} {self.follow} - ${self.unfollow}>'

class AutoFollow(models.Model):
  """ Model for recurring tasks """
  id = models.AutoField(primary_key=True)
  user = models.ForeignKey(User, on_delete=models.CASCADE)
  path = models.CharField(
    "file path",
    max_length=255, null=False,
    validators=[validate_path], default="screener.csv")
  min_friend_follower_overlap = models.FloatField(
    "min friend follower overlap", null=False,
    validators=[MinValueValidator(0.0), MaxValueValidator(1.0)], default=0.5)
  schedule = models.CharField(
    "crontab schedule",
    max_length=128, null=False,
    validators=[validate_schedule], default="0 0 * * *")
  count = models.PositiveIntegerField("count", null=False)
  over_hours = models.FloatField("over hours",
    null=False, validators=[MinValueValidator(0.0)], default=1.0)
  unfollow_days = models.PositiveIntegerField("unfollow days",
    null=True, blank=True, default=settings.follow.unfollow_default_days)
