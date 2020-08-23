""" date_utils.py """
from datetime import datetime

DATE_FORMAT = "%Y-%m-%d %H:%M"

def format_date(date: datetime = datetime.now()) -> str:
  """ converts a date to a string, defaults to now """
  return date.strftime(DATE_FORMAT)

def read_date(date: str) -> 'datetime':
  """ Converts a string to a date """
  return datetime.strptime(date, DATE_FORMAT)
