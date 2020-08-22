""" models.py """

from django.db import models

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
  username = models.CharField(max_length=240, null=False, unique=True)
  follow = models.DateTimeField('date to follow', null=True, blank=True)
  unfollow = models.DateTimeField('date to unfollow', null=True, blank=True)
  followed = models.DateTimeField('date did follow', null=True, blank=True)
  unfollowed = models.DateTimeField('date did unfollow', null=True, blank=True)

  def __str__(self):
    return f'<Follow {self.username} {self.follow} - ${self.unfollow}>'
