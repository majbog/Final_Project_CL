# -*- coding: utf-8 -*-
# Generated by Django 1.11.11 on 2018-03-21 09:11
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import mng_dashboard.models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Employee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=64)),
                ('last_name', models.CharField(max_length=64)),
                ('email', models.CharField(max_length=64, validators=[mng_dashboard.models.validate_emp_mail])),
                ('active', models.NullBooleanField(default=True)),
                ('int_id', models.CharField(max_length=8)),
            ],
        ),
        migrations.CreateModel(
            name='Productivity',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('number', models.IntegerField()),
                ('type', models.IntegerField(choices=[(1, b'Inbound call'), (2, b'Outbound call'), (3, b'Inbound email'), (4, b'Outbound email')])),
                ('clerk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mng_dashboard.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='Territory',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
                ('clerks', models.ManyToManyField(to='mng_dashboard.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='TerritoryResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('result', models.DecimalField(decimal_places=2, max_digits=15)),
                ('territory', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mng_dashboard.Territory')),
            ],
        ),
        migrations.CreateModel(
            name='TimeExp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('type', models.IntegerField(choices=[(1, b'Sick Leave'), (2, b'Vacation'), (3, b'Training'), (4, b'Overtime')])),
                ('clerk', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='mng_dashboard.Employee')),
            ],
        ),
        migrations.CreateModel(
            name='UnallocatedResults',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('unallocated_cash', models.DecimalField(decimal_places=2, max_digits=15)),
            ],
        ),
    ]
