""" edit.py """

from django import forms
from django.http import HttpResponse, HttpResponseRedirect
from django.template import loader
from django.urls import reverse

from twitter.models import Follow


def edit_follow(request, id: int):
  """ edits a follow """
  template = loader.get_template('create/index.html')
  form = EditFollowForm(request.POST)
  instance = Follow.objects.get(id=id)
  if request.method == "POST":
    form = EditFollowForm(request.POST, instance=instance)
    if form.is_valid():
      form.save(commit=True)
      return HttpResponseRedirect(reverse('twitter:manage'))
  else:
    form = EditFollowForm(instance=instance)

  context = {
    'id': id,
    'form': form,
    'type': "follow",
    'title': 'Edit Follow'
  }
  return HttpResponse(template.render(context, request))

class EditFollowForm(forms.ModelForm):
  """ Form to edit a scheduled tweet """
  def __init__(self, *args, **kwargs):
    super(EditFollowForm, self).__init__(*args, **kwargs)
    readonly_fields = ['followed', 'unfollowed']
    for field in readonly_fields:
      self.fields[field].widget.attrs['readonly'] = True

  class Meta:
    model = Follow
    fields = ('user', 'username', 'follow', 'unfollow', 'followed', 'unfollowed',)
