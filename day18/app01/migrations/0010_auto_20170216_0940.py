# -*- coding: utf-8 -*-
# Generated by Django 1.10.4 on 2017-02-16 01:40
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app01', '0009_remove_post_title'),
    ]

    operations = [
        migrations.AlterField(
            model_name='post',
            name='catalog',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='posts', to='app01.Catalog'),
        ),
    ]
