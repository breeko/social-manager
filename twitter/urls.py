""" urls.py """
from django.urls import path
from twitter.views import *

urlpatterns = [
    path('', index, name='index'),
    path('user', user, name='user'),
    path('manage', manage, name='manage'),
    path('create', create, name='create'),
    path('follow', follow, name='follow'),
    path('auto_follow', auto_follow, name='auto_follow'),
    path('parse_crontab', parse_crontab, name='parse_crontab'),
    path('news', news, name='news'),
    path('logs', logs, name='logs'),
    path(r'tweet/follow/bulk', bulk_follow, name='bulk_follow'),
    path(r'follow/delete', delete_follows, name='delete_follows'),
    path(r'follow/reschedule', reschedule_follows, name='reschedule_follows'),
    path(r'tweet/delete', delete_tweets, name='delete_tweets'),
    path(r'tweet/edit/<int:id>', create, name='edit_tweet'),
    path(r'follow/edit/<int:id>', edit_follow, name='edit_follow'),
    path(r'user/edit/<int:id>', user, name='edit_user'),
    path(r'tweet/reschedule', reschedule_tweets, name='reschedule_tweets'),
    path(r'auto_follow/edit/<int:id>', auto_follow, name='edit_auto_follow'),
    path(r'auto_follow/delete', delete_auto_follows, name='delete_auto_follows'),
]
