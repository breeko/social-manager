""" edit.py """


from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.template import loader
from django.urls import reverse
from django.utils.html import mark_safe

from cron_descriptor import ExpressionDescriptor
from twitter.models import AutoFollow


def auto_follow(request, id: int = None):
  """ recurring tasks """
  template = loader.get_template("auto_follow/index.html")
  instance = None
  if id is not None:
    instance = get_object_or_404(AutoFollow, id=id)

  if request.method == "POST":
    form = AutoFollowForm(request.POST, instance=instance)
    if form.is_valid():
      form.save(commit=True)
      if id is None:
        return HttpResponseRedirect(reverse("twitter:auto_follow"))
      return HttpResponseRedirect(reverse("twitter:manage"))
  else:
    form = AutoFollowForm(instance=instance)

  context = {
    "id": id,
    "form": form,
    "title": "Create Auto Follow" if id is None else "Edit Auto Follow",
    "path": "twitter:auto_follow"
  }
  return HttpResponse(template.render(context, request))

class AutoFollowForm(forms.ModelForm):
  """ Form to edit a scheduled tweet """
  class Meta:
    model = AutoFollow
    fields = ("user", "path", "min_friend_follower_overlap", "count", "over_hours", "unfollow_days", "schedule")

def parse_crontab(request):
  """ Deletes a given follow id """
  value = request.POST.get("value", "")
  description = ExpressionDescriptor(value, throw_exception_on_parse_error=False)
  return HttpResponse(description)
