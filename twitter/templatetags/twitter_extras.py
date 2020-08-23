""" twitter_extras.py"""

from datetime import datetime, timedelta
from random import random
from urllib.parse import urlparse

from django import template

from twitter.utils.date_utils import format_date, read_date

register = template.Library()

@register.filter
def addstr(arg1, arg2):
  """concatenate arg1 & arg2"""
  return str(arg1) + str(arg2)

@register.filter
def month_year(date: datetime) -> str:
  """returns month-year of given date"""
  if not isinstance(date, datetime):
    return date
  return date.strftime('%m-%Y')


@register.filter
def get_domain(url: str) -> str:
  """ returns the domain given a url
    e.g. f(http://stackoverflow.com/questions/1234567/blah) => 'stackoverflow.com'
  """
  parsed_uri = urlparse(url)
  return parsed_uri.netloc.replace('www.', '')

@register.filter
def comma_number(value) -> str:
  """ converts a number to a comma separated value
    e.g. f(10000) -> 10,000
  """
  if type(value) in [float, int]:
    return f'{value:,}'
  return value

@register.filter
def randomize_time(value) -> str:
  """ Randomizes the time by adding up to an hour
    e.g. f(8:35) => 8:42
  """
  if not isinstance(value, str):
    return value
  try:
    date = read_date(value)
    date += timedelta(hours=random())
    date_value = format_date(date)
    return date_value
  except ValueError:
    return value
