# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0007_auto_20180419_0832'),
    ]

    operations = [
        migrations.AddField(
            model_name='myuser',
            name='admin',
            field=models.BooleanField(default=False),
        ),
    ]
