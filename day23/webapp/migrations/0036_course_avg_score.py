# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-06-12 02:44
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0035_auto_20170202_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='course',
            name='avg_score',
            field=models.PositiveIntegerField(default=0),
        ),
    ]
