# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-04 09:52
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0053_codcaus'),
    ]

    operations = [
        migrations.AddField(
            model_name='f412',
            name='codigoCausa',
            field=models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='f412.codCaus'),
        ),
    ]
