import requests
from bs4 import BeautifulSoup
from requests.utils import quote
import re
import tweepy
from twitter.models import User
from tweepy.api import API
from typing import List

def generate_tweet(word: str) -> str:
  url = f"https://thoughts.sushant-kumar.com/{quote(word)}"
  response = requests.get(url)
  soup = BeautifulSoup(response.text, "lxml")
  out = soup.blockquote.text.replace("\n","")[1:-1]
  return out

def get_api(user: User) -> API:
  auth = tweepy.OAuthHandler(user.api_key, user.api_secret)
  auth.set_access_token(user.api_access_token, user.api_token_secret)
  api = tweepy.API(auth)
  return api

def get_trends(user: User) -> List[str]:
  api = get_api(user)
  US_CODE = 23424977
  trends = api.trends_available()
  [t for t in trends if t['name'] == 'United States']
  trends = api.trends_place(US_CODE)
  trends_names = [n.get('name') for n in trends[0]['trends']]
  return trends_names
