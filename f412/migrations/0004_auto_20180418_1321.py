# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0003_auto_20180418_1301'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sgm',
            name='seccion',
        ),
        migrations.AddField(
            model_name='sgm',
            name='seccion',
            field=models.ManyToManyField(to='f412.Seccion', default=1),
        ),
    ]
