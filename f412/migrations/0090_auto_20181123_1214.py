# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-11-23 11:14
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0089_auto_20181123_1105'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='reasontree',
            name='currentlyInUse',
        ),
        migrations.RemoveField(
            model_name='reasontreefield',
            name='currentlyInUse',
        ),
    ]
