# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-20 03:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0010_auto_20170120_1148'),
    ]

    operations = [
        migrations.AlterField(
            model_name='studentinfo',
            name='courses',
            field=models.ManyToManyField(blank=True, to='webapp.Course'),
        ),
    ]
