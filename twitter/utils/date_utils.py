""" date_utils.py """
from datetime import datetime, timedelta
from random import random

from django.utils import timezone

DATE_FORMAT = "%Y-%m-%d %H:%M"

def format_date(date: datetime = timezone.now()) -> str:
  """ converts a date to a string, defaults to now """
  return date.strftime(DATE_FORMAT)

def read_date(date: str) -> 'datetime':
  """ Converts a string to a date """
  return datetime.strptime(date, DATE_FORMAT)

def within_hour(dt: datetime = timezone.now(), hours: float = 1.0) -> 'datetime':
  """ Returns a datetime object that's within in the next hour """
  return dt + timedelta(hours=random() * hours)
