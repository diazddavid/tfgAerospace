# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0010_auto_20180423_0938'),
    ]

    operations = [
        migrations.AddField(
            model_name='f412',
            name='accion',
            field=models.CharField(max_length=512, default=''),
        ),
    ]
