# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-13 14:16
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0002_auto_20170213_1145'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='head_pic',
            field=models.TextField(blank=True, null=True),
        ),
    ]
