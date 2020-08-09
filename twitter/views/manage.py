from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from ..models import Tweet, User
from django.template import loader
from django import forms
from django.urls import reverse

def manage(request):
    template = loader.get_template('manage/index.html')
    tweets = Tweet.objects.order_by('scheduled').all()
    
    context = {
        'tweets': tweets,
        'delete_tweet': delete_tweet,
        'title': 'Manage'
    }
    return HttpResponse(template.render(context, request))

def delete_tweet(request, pk):
    tweet = Tweet.objects.get(id=pk)
    if tweet:
        tweet.delete()
    return HttpResponseRedirect(reverse('twitter:manage'))

