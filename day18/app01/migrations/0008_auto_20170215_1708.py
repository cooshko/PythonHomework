# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-15 09:08
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0007_auto_20170215_1707'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='like_count',
            field=models.PositiveIntegerField(default=1),
        ),
    ]