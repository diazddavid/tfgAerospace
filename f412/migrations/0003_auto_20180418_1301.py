# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0002_defecto_seccion'),
    ]

    operations = [
        migrations.CreateModel(
            name='Pieza',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.RemoveField(
            model_name='area',
            name='seccion',
        ),
        migrations.AddField(
            model_name='area',
            name='seccion',
            field=models.ManyToManyField(to='f412.Seccion', default=1),
        ),
        migrations.RemoveField(
            model_name='defecto',
            name='seccion',
        ),
        migrations.AddField(
            model_name='defecto',
            name='seccion',
            field=models.ManyToManyField(to='f412.Seccion', default=1),
        ),
        migrations.AddField(
            model_name='f412',
            name='pieza',
            field=models.ForeignKey(default=1, to='f412.Pieza'),
        ),
    ]
