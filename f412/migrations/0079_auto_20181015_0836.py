# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-10-15 06:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0078_f412_hnc'),
    ]

    operations = [
        migrations.AlterField(
            model_name='f412',
            name='hnc',
            field=models.CharField(default='', max_length=64),
        ),
    ]
