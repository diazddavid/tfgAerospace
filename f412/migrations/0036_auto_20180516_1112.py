# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-05-16 09:12
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0035_auto_20180516_1112'),
    ]

    operations = [
        migrations.AlterField(
            model_name='f412',
            name='Estado',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='f412.Estado'),
        ),
    ]
