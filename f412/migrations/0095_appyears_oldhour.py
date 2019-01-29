# -*- coding: utf-8 -*-
# Generated by Django 1.10.5 on 2018-12-12 10:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('f412', '0094_planescount'),
    ]

    operations = [
        migrations.CreateModel(
            name='appYears',
            fields=[
                ('year', models.IntegerField(primary_key=True, serialize=False)),
            ],
        ),
        migrations.CreateModel(
            name='oldHour',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=1)),
                ('month', models.IntegerField(default=1)),
                ('hours', models.FloatField(default=0.0)),
                ('codCaus', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='f412.codCaus')),
                ('component', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='f412.Componente')),
                ('program', models.ForeignKey(default=1, on_delete=django.db.models.deletion.CASCADE, to='f412.Programa')),
            ],
        ),
    ]
