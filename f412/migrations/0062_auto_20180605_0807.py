# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-05 06:07
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0061_merge_20180605_0807'),
    ]

    operations = [
        migrations.AlterField(
            model_name='f412',
            name='operacion',
            field=models.IntegerField(default=1),
        ),
    ]
