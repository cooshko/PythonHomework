# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-26 15:26
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0017_auto_20170126_1541'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessiontokens',
            name='token',
            field=models.CharField(max_length=64, unique=True),
        ),
    ]
