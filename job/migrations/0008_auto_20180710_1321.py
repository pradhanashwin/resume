# Generated by Django 2.0.7 on 2018-07-10 07:36

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0007_auto_20180710_1320'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='applicant',
            name='email',
        ),
        migrations.RemoveField(
            model_name='applicant',
            name='name',
        ),
    ]
