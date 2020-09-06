""" admin.py """
from django.contrib import admin
from .models import User, Tweet, Follow, AutoFollow

# Register your models here.
admin.site.register(User)
admin.site.register(Tweet)
admin.site.register(Follow)
admin.site.register(AutoFollow)
