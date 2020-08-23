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
    path(r'tweet/bulk_follow', bulk_follow, name='bulk_follow'),
    path(r'tweet/delete_follow/(?P<pk>[0-9]+)', delete_follow, name='delete_follow'),
    path(r'tweet/create_tweet', submit_create_tweet, name='create_tweet'),
    path(r'tweet/delete/(?P<pk>[0-9]+)', delete_tweet, name='delete_tweet'),
    path(r'tweet/edit/(?P<tweet_id>[0-9]+)', edit_tweet, name='edit_tweet'),
    path(r'tweet/edit/<int:tweet_id>', edit_tweet, name='edit_tweet'),
]
