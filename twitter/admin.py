from django.contrib import admin
from .models import User, Tweet, Follow

# Register your models here.
admin.site.register(User)
admin.site.register(Tweet)
admin.site.register(Follow)
