# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-06-04 14:53
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0058_remove_f412_operacion'),
    ]

    operations = [
        migrations.RenameField(
            model_name='f412',
            old_name='operacionChar',
            new_name='operacion',
        ),
    ]
