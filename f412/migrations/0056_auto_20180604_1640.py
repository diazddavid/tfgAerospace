# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-04 14:40
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0055_auto_20180604_1636'),
    ]

    operations = [
        migrations.AddField(
            model_name='f412',
            name='operacionChar',
            field=models.CharField(default='', max_length=128),
        ),
        migrations.AlterField(
            model_name='f412',
            name='operacion',
            field=models.IntegerField(default=1),
        ),
    ]
