# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-01-27 06:34
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('webapp', '0019_auto_20170126_2333'),
    ]

    operations = [
        migrations.AlterField(
            model_name='sessiontokens',
            name='staff',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='webapp.StaffInfo'),
        ),
    ]