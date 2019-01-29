# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Area',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Componente',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Defecto',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Designacion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('Componente', models.ForeignKey(to='f412.Componente', default=1)),
            ],
        ),
        migrations.CreateModel(
            name='Estado',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='F412',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('Fecha', models.DateField()),
                ('horas', models.CharField(default='', max_length=64)),
                ('Referencia', models.CharField(default='', max_length=128)),
                ('Descripcion', models.CharField(default='', max_length=512)),
                ('Area', models.ForeignKey(to='f412.Area')),
                ('Componente', models.ForeignKey(to='f412.Componente')),
                ('Defecto', models.ForeignKey(to='f412.Defecto')),
                ('Designacion', models.ForeignKey(to='f412.Designacion')),
                ('Estado', models.ForeignKey(to='f412.Estado')),
            ],
        ),
        migrations.CreateModel(
            name='myUser',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('email', models.CharField(max_length=256)),
                ('puedeCrear', models.BooleanField(default=False)),
                ('passwd', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='PN',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('Designacion', models.OneToOneField(default=1, to='f412.Designacion')),
            ],
        ),
        migrations.CreateModel(
            name='Programa',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
            ],
        ),
        migrations.CreateModel(
            name='Seccion',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('programa', models.ForeignKey(to='f412.Programa', default=1)),
            ],
        ),
        migrations.CreateModel(
            name='SGM',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('number', models.CharField(max_length=128)),
                ('name', models.CharField(max_length=128)),
                ('seccion', models.ForeignKey(to='f412.Seccion', default=1)),
            ],
        ),
        migrations.AddField(
            model_name='pn',
            name='programa',
            field=models.ForeignKey(to='f412.Programa', default=1),
        ),
        migrations.AddField(
            model_name='myuser',
            name='programa',
            field=models.ManyToManyField(to='f412.Programa'),
        ),
        migrations.AddField(
            model_name='myuser',
            name='seccion',
            field=models.ForeignKey(to='f412.Seccion', default=1),
        ),
        migrations.AddField(
            model_name='myuser',
            name='user',
            field=models.OneToOneField(to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='f412',
            name='LastChangeUser',
            field=models.ForeignKey(related_name='f412_requests_created', default=1, to='f412.myUser'),
        ),
        migrations.AddField(
            model_name='f412',
            name='PN',
            field=models.ForeignKey(to='f412.PN'),
        ),
        migrations.AddField(
            model_name='f412',
            name='SGM',
            field=models.ForeignKey(to='f412.SGM', default=1),
        ),
        migrations.AddField(
            model_name='f412',
            name='Usuario',
            field=models.ForeignKey(to='f412.myUser'),
        ),
        migrations.AddField(
            model_name='f412',
            name='programa',
            field=models.ForeignKey(to='f412.Programa', default=1),
        ),
        migrations.AddField(
            model_name='f412',
            name='seccion',
            field=models.ForeignKey(to='f412.Seccion', default=1),
        ),
        migrations.AddField(
            model_name='componente',
            name='programa',
            field=models.ForeignKey(to='f412.Programa', default=1),
        ),
        migrations.AddField(
            model_name='area',
            name='seccion',
            field=models.ForeignKey(to='f412.Seccion', default=1),
        ),
    ]
