# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-05 10:21
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0067_auto_20180605_0912'),
    ]

    operations = [
        migrations.AddField(
            model_name='f412',
            name='rtMod',
            field=models.BooleanField(default=False),
        ),
    ]
