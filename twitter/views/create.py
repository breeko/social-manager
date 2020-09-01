""" edit.py """

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse
from django.shortcuts import get_object_or_404

from twitter.models import Tweet


def create(request, id: int = None):
  """ edits a tweet """
  template = loader.get_template("create/index.html")
  form = CreateTweetForm(request.POST)
  instance = None
  if id is not None:
    instance = get_object_or_404(Tweet, id=id)

  if request.method == "POST":
    form = CreateTweetForm(request.POST, instance=instance)
    if form.is_valid():
      form.save(commit=True)
      if id is None:
        return HttpResponseRedirect(reverse("twitter:create"))
      return HttpResponseRedirect(reverse("twitter:manage"))
  else:
    form = CreateTweetForm(instance=instance)

  context = {
    "id": id,
    "form": form,
    "title": "Create" if id is None else "Edit"
  }
  return HttpResponse(template.render(context, request))

class CreateTweetForm(forms.ModelForm):
  """ Form to edit a scheduled tweet """
  class Meta:
    model = Tweet
    fields = ("user", "body", "scheduled",)
    widgets = {
      "body": forms.Textarea(attrs={"rows": 4}),
    }
