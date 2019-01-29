# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0005_f412_myid'),
    ]

    operations = [
        migrations.AddField(
            model_name='f412',
            name='nAV',
            field=models.IntegerField(default=1),
        ),
    ]
