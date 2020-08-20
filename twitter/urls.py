""" urls.py """
from django.urls import path
from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('users', users, name='users'),
    path('create', create, name='create'),
    path('manage', manage, name='manage'),
    path('generate', generate, name='generate'),
    path('follow', follow, name='follow'),
    path('news', news, name='news'),
    path(r'tweet/delete_follow/(?P<pk>[0-9]+)', delete_follow, name='delete_follow'),
    path(r'tweet/delete/(?P<pk>[0-9]+)', delete_tweet, name='delete_tweet'),
    path(r'tweet/edit/(?P<tweet_id>[0-9]+)', edit_tweet, name='edit_tweet'),
    path(r'tweet/edit/<int:tweet_id>', edit_tweet, name='edit_tweet'),
    path(r'ajax/hi', say_hi, name='say_hi'),
]
