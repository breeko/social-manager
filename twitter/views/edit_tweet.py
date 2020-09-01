""" edit.py """

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.models import Tweet


def edit_tweet(request, id: int):
  """ edits a tweet """
  template = loader.get_template("edit/index.html")
  form = EditTweetForm(request.POST)
  instance = Tweet.objects.get(id=id)
  if request.method == "POST":
    form = EditTweetForm(request.POST, instance=instance)
    if form.is_valid():
      form.save(commit=True)
      return HttpResponseRedirect(reverse("twitter:manage"))
  else:
    form = EditTweetForm(instance=instance)

  context = {
    "id": id,
    "form": form,
    "title": "Edit Tweet",
    "path": "twitter:edit_tweet"
  }
  return HttpResponse(template.render(context, request))

class EditTweetForm(forms.ModelForm):
  """ Form to edit a scheduled tweet """
  class Meta:
    model = Tweet
    fields = ("user", "body", "scheduled",)
    widgets = {
      "body": forms.Textarea(attrs={"rows": 4}),
    }
