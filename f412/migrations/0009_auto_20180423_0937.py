# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0008_myuser_admin'),
    ]

    operations = [
        migrations.AlterField(
            model_name='f412',
            name='Fecha',
            field=models.DateTimeField(auto_now_add=True),
        ),
    ]
