# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-15 06:01
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0029_reasontreefield_shortname'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='NG',
            field=models.CharField(default='', max_length=64),
        ),
    ]
