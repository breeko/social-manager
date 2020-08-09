# Generated by Django 3.1 on 2020-08-07 09:11

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('username', models.CharField(max_length=80, unique=True)),
                ('api_key', models.CharField(max_length=80, unique=True)),
                ('api_secret', models.CharField(max_length=80, unique=True)),
                ('api_access_token', models.CharField(max_length=80, unique=True)),
                ('api_token_secret', models.CharField(max_length=80, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tweet',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('body', models.CharField(max_length=240)),
                ('created', models.DateTimeField(auto_now_add=True, verbose_name='date created')),
                ('modified', models.DateTimeField(auto_now=True, verbose_name='date modified')),
                ('scheduled', models.DateTimeField(verbose_name='date scheduled')),
                ('sent', models.DateTimeField(verbose_name='date sent')),
                ('deleted', models.DateTimeField(verbose_name='date deleted')),
                ('user_id', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='twitter.user')),
            ],
        ),
    ]
