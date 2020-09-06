# Generated by Django 3.1 on 2020-09-04 12:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('twitter', '0007_user_rapidapi_key'),
    ]

    operations = [
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('task_type', models.CharField(choices=[('AF', 'Auto Follow')], max_length=2)),
            ],
        ),
        migrations.AlterField(
            model_name='follow',
            name='username',
            field=models.CharField(max_length=240),
        ),
    ]