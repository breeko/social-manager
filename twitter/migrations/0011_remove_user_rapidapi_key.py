# Generated by Django 3.1 on 2020-09-08 10:57

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0010_auto_20200906_1446'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='rapidapi_key',
        ),
    ]
