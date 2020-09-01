""" screener_utils .py """
from time import sleep

import tweepy


def get_overlap(api: tweepy.API, name: str) -> float:
  """ Returns the """
  friends = set()
  followers = set()
  for page in tweepy.Cursor(api.friends_ids, screen_name=name).pages():
    friends = friends | set(page)
    sleep(5)
  for page in tweepy.Cursor(api.followers_ids, screen_name=name).pages():
    followers = followers | set(page)
    sleep(5)
  if len(followers) == 0:
    return 0
  score = len(followers.intersection(friends)) / len(followers)
  return score


def flatten_dict(init, lkey=''):
  """ Flattens a dictionary, ignoring nested lists
  e.g. f({a: {b: 1, c: [2, 3]}, d: 4}) => {a_b: 1, a_c: [...], d: 4}
  """
  ret = {}
  for rkey,val in init.items():
    key = lkey+rkey
    if isinstance(val, dict):
      ret.update(flatten_dict(val, key+'_'))
    elif isinstance(val, list):
      ret[key] = "[...]"
    else:
      ret[key] = val
  return ret

""" orderings.py """

column_orderings = [
  "id",
  "id_str",
  "name",
  "screen_name",
  "location",
  "profile_location",
  "description",
  "url",
  "entities_description_urls",
  "protected",
  "followers_count",
  "friends_count",
  "listed_count",
  "created_at",
  "favourites_count",
  "utc_offset",
  "time_zone",
  "geo_enabled",
  "verified",
  "statuses_count",
  "lang",
  "status_created_at",
  "status_id",
  "status_id_str",
  "status_text",
  "status_truncated",
  "status_entities_hashtags",
  "status_entities_symbols",
  "status_entities_user_mentions",
  "status_entities_urls",
  "status_source",
  "status_in_reply_to_status_id",
  "status_in_reply_to_status_id_str",
  "status_in_reply_to_user_id",
  "status_in_reply_to_user_id_str",
  "status_in_reply_to_screen_name",
  "status_geo",
  "status_coordinates",
  "status_place",
  "status_contributors",
  "status_retweeted_status_created_at",
  "status_retweeted_status_id",
  "status_retweeted_status_id_str",
  "status_retweeted_status_text",
  "status_retweeted_status_truncated",
  "status_retweeted_status_entities_hashtags",
  "status_retweeted_status_entities_symbols",
  "status_retweeted_status_entities_user_mentions",
  "status_retweeted_status_entities_urls",
  "status_retweeted_status_source",
  "status_retweeted_status_in_reply_to_status_id",
  "status_retweeted_status_in_reply_to_status_id_str",
  "status_retweeted_status_in_reply_to_user_id",
  "status_retweeted_status_in_reply_to_user_id_str",
  "status_retweeted_status_in_reply_to_screen_name",
  "status_retweeted_status_geo",
  "status_retweeted_status_coordinates",
  "status_retweeted_status_place",
  "status_retweeted_status_contributors",
  "status_retweeted_status_is_quote_status",
  "status_retweeted_status_quoted_status_id",
  "status_retweeted_status_quoted_status_id_str",
  "status_retweeted_status_retweet_count",
  "status_retweeted_status_favorite_count",
  "status_retweeted_status_favorited",
  "status_retweeted_status_retweeted",
  "status_retweeted_status_possibly_sensitive",
  "status_retweeted_status_lang",
  "status_is_quote_status",
  "status_quoted_status_id",
  "status_quoted_status_id_str",
  "status_retweet_count",
  "status_favorite_count",
  "status_favorited",
  "status_retweeted",
  "status_lang",
  "contributors_enabled",
  "is_translator",
  "is_translation_enabled",
  "profile_background_color",
  "profile_background_image_url",
  "profile_background_image_url_https",
  "profile_background_tile",
  "profile_image_url",
  "profile_image_url_https",
  "profile_banner_url",
  "profile_link_color",
  "profile_sidebar_border_color",
  "profile_sidebar_fill_color",
  "profile_text_color",
  "profile_use_background_image",
  "has_extended_profile",
  "default_profile",
  "default_profile_image",
  "following",
  "follow_request_sent",
  "notifications",
  "translator_type"
]
