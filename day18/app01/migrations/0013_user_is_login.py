# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2017-02-20 13:23
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0012_auto_20170217_2152'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_login',
            field=models.BooleanField(default=False),
        ),
    ]
