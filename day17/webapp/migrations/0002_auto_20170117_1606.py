# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-17 08:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentinfo',
            name='email',
            field=models.EmailField(blank=True, max_length=254, null=True),
        ),
        migrations.AddField(
            model_name='studentinfo',
            name='password',
            field=models.CharField(default=1, max_length=256),
            preserve_default=False,
        ),
    ]
