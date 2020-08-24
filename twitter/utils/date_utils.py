""" date_utils.py """
from datetime import datetime, timedelta
from random import random

DATE_FORMAT = "%Y-%m-%d %H:%M"

def format_date(date: datetime = datetime.now()) -> str:
  """ converts a date to a string, defaults to now """
  return date.strftime(DATE_FORMAT)

def read_date(date: str) -> 'datetime':
  """ Converts a string to a date """
  return datetime.strptime(date, DATE_FORMAT)

def this_hour() -> 'datetime':
  """ Returns a datetime object that's within in the next hour """
  return datetime.now() + timedelta(hours = random())
