# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='defecto',
            name='seccion',
            field=models.ForeignKey(default=1, to='f412.Seccion'),
        ),
    ]
