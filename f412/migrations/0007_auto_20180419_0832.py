# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0006_f412_nav'),
    ]

    operations = [
        migrations.AlterField(
            model_name='f412',
            name='Designacion',
            field=models.ForeignKey(to='f412.Designacion', default=1),
        ),
    ]
