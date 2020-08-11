from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from ..models import Tweet, User
from django.template import loader
from django import forms
from django.urls import reverse
from social.settings import TWEET_SHOW_OLD

def manage(request):
    template = loader.get_template('manage/index.html')
    sent = Tweet.objects.filter(sent__isnull=False).order_by('-scheduled')[:TWEET_SHOW_OLD]
    not_sent = Tweet.objects.filter(sent__isnull=True)
    tweets = sent | not_sent

    context = {
        'tweets': tweets.order_by('scheduled'),
        'delete_tweet': delete_tweet,
        'title': 'Manage'
    }
    return HttpResponse(template.render(context, request))

def delete_tweet(request, pk):
    tweet = Tweet.objects.get(id=pk)
    if tweet:
        tweet.delete()
    return HttpResponseRedirect(reverse('twitter:manage'))

