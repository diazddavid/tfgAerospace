# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-10 10:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0022_auto_20180509_0807'),
    ]

    operations = [
        migrations.AddField(
            model_name='estado',
            name='color',
            field=models.CharField(default=1, max_length=128),
        ),
    ]
