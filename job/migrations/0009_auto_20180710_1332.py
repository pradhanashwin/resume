# Generated by Django 2.0.7 on 2018-07-10 07:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('job', '0008_auto_20180710_1321'),
    ]

    operations = [
        migrations.AlterField(
            model_name='applicant',
            name='resume',
            field=models.FileField(upload_to='uploads/resume/%Y/%m/%d/'),
        ),
    ]