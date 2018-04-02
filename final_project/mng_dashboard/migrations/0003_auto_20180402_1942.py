# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-04-02 19:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mng_dashboard', '0002_auto_20180321_0912'),
    ]

    operations = [
        migrations.CreateModel(
            name='MailStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sent', models.IntegerField()),
                ('received', models.IntegerField()),
                ('backlog', models.IntegerField()),
            ],
        ),
        migrations.AlterField(
            model_name='productivity',
            name='type',
            field=models.IntegerField(choices=[(1, 'Inbound call'), (2, 'Outbound call'), (3, 'Inbound email'), (4, 'Outbound email')]),
        ),
        migrations.AlterField(
            model_name='timeexp',
            name='type',
            field=models.IntegerField(choices=[(1, 'Sick Leave'), (2, 'Vacation'), (3, 'Training'), (4, 'Overtime')]),
        ),
    ]
