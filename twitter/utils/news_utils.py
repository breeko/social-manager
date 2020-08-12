""" news_utils.py """
from typing import List
from newscatcher import Newscatcher

TOPIC_CHOICES = [
  'tech',
  'news',
  'business',
  'science',
  'finance',
  'food',
  'politics',
  'economics',
  'travel',
  'entertainment',
  'music',
  'sport',
  'world'
]

def get_news(sites: List[str], topic: str):
  """ Returns all the news given a list of sites and a topic
    e.g. get_news(['nytimes.com'], topic='tech') => [{title: ..., title_detail: ...}, ...]
  """
  if topic not in TOPIC_CHOICES:
    return []
  out = []
  for site in sites:
    news_catcher = Newscatcher(site, topic=topic)
    news = news_catcher.get_news()
    if isinstance(news, dict):
      out.extend(news.get('articles'))
  return out
