""" urls.py """
from django.urls import path
from twitter.views import *

urlpatterns = [
    path('', index, name='index'),
    path('users', users, name='users'),
    path('manage', manage, name='manage'),
    path('generate', generate, name='generate'),
    path('follow', follow, name='follow'),
    path('news', news, name='news'),
    path('logs', logs, name='logs'),
    path(r'tweet/follow/bulk', bulk_follow, name='bulk_follow'),
    path(r'follow/delete', delete_follows, name='delete_follows'),
    path(r'follow/reschedule', reschedule_follows, name='reschedule_follows'),
    path(r'tweet/create_tweet', submit_create_tweet, name='create_tweet'),
    path(r'tweet/delete', delete_tweets, name='delete_tweets'),
    path(r'tweet/edit/<int:id>', edit_tweet, name='edit_tweet'),
    path(r'tweet/reschedule', reschedule_tweets, name='reschedule_tweets'),
]
