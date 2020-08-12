""" twitter_extras.py"""

from datetime import datetime
from urllib.parse import urlparse

from django import template

register = template.Library()

@register.filter
def addstr(arg1, arg2):
  """concatenate arg1 & arg2"""
  return str(arg1) + str(arg2)

@register.filter
def month_year(date: datetime) -> str:
  """returns month-year of given date"""
  if isinstance(date, datetime):
    return ""
  return date.strftime('%m-%Y')


@register.filter
def get_domain(url: str) -> str:
  """ returns the domain given a url
    e.g. f(http://stackoverflow.com/questions/1234567/blah) => 'stackoverflow.com'
  """
  parsed_uri = urlparse(url)
  return parsed_uri.netloc.replace('www.', '')
