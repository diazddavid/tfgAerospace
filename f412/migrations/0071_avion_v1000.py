# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-12 08:50
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0070_auto_20180611_1112'),
    ]

    operations = [
        migrations.AddField(
            model_name='avion',
            name='v1000',
            field=models.BooleanField(default=False),
        ),
    ]
