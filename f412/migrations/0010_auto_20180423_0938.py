# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0009_auto_20180423_0937'),
    ]

    operations = [
        migrations.AlterField(
            model_name='f412',
            name='Fecha',
            field=models.DateField(),
        ),
    ]
