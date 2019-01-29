# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0004_auto_20180418_1321'),
    ]

    operations = [
        migrations.AddField(
            model_name='f412',
            name='myID',
            field=models.IntegerField(default=1),
        ),
    ]
